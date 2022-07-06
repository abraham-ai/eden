import os
import sys
import git
import json
import warnings
import uvicorn
import logging
import threading
import traceback
from fastapi import FastAPI
from prometheus_client import Gauge
from starlette_exporter import PrometheusMiddleware, handle_metrics
from fastapi.middleware.cors import CORSMiddleware

from .datatypes import Image
from .queue import QueueData
from .log_utils import Colors
from .models import Credentials, WaitFor
from .result_storage import ResultStorage
from .config_wrapper import ConfigWrapper
from .data_handlers import Encoder, Decoder
from .threaded_server import ThreadedServer
from .progress_tracker import fetch_progress_from_token
from .log_utils import log_levels, celery_log_levels, PREFIX
from .prometheus_utils import PrometheusMetrics

from .utils import stop_everything_gracefully, generate_random_string

from uvicorn.config import LOGGING_CONFIG

"""
Celery+redis is needed to be able to queue tasks
"""
from celery import Celery
from celery.result import AsyncResult
from .celery_utils import run_celery_app

"""
tool to allocate gpus on queued tasks
"""
from .gpu_allocator import GPUAllocator


def host_block(
    block,
    port=8080,
    host="0.0.0.0",
    max_num_workers=4,
    redis_port=6379,
    redis_host="localhost",
    requires_gpu=True,
    log_level="warning",
    logfile="logs.log",
    exclude_gpu_ids: list = [],
    remove_result_on_fetch = False
):
    """
    Use this to host your eden.Block on a server. Supports multiple GPUs and queues tasks automatically with celery.

    Args:
        block (eden.block.Block): The eden block you'd want to host.
        port (int, optional): Localhost port where the block would be hosted. Defaults to 8080.
        host (str): specifies where the endpoint would be hosted. Defaults to '0.0.0.0'.
        max_num_workers (int, optional): Maximum number of tasks to run in parallel. Defaults to 4.
        redis_port (int, optional): Port number for celery's redis server. Defaults to 6379.
        redis_host (str, optional): Place to host redis for `eden.queue.QueueData`. Defaults to localhost.
        requires_gpu (bool, optional): Set this to False if your tasks dont necessarily need GPUs.
        log_level (str, optional): Can be 'debug', 'info', or 'warning'. Defaults to 'warning'
        logfile(str, optional): Name of the file where the logs would be stored. If set to None, it will show all logs on stdout. Defaults to 'logs.log'
        exclude_gpu_ids (list, optional): List of gpu ids to not use for hosting. Example: [2,3]
    """

    """
    Response templates: 
    
    /run: 
        {
            'token': some_long_token,
        }

    /fetch: 
        if task is queued:
            {
                'status': {
                    'status': queued,
                    'queue_position': int
                },
                config: current_config
            }

        elif task is running:
            {
                'status': {
                    'status': 'running',
                    'progress': float between 0 and 1,

                },
                config: current_config,
                'output': {}  ## optionally the user should be able to write outputs here
            }
        elif task failed:
            {
                'status': {
                    'status': 'failed',                    
                }
                'config': current_config,
                'output': {}  ## will still include the outputs if any so that it gets returned even though the task failed
            }
        elif task succeeded:
            {
                'status': {
                    'status': 'complete'
                },
                'output': user_output,
                'config': config
            }
    """

    """
    Initiating celery app
    """
    celery_app = Celery(__name__, broker=f"redis://{redis_host}:{str(redis_port)}")
    celery_app.conf.broker_url = os.environ.get(
        "CELERY_BROKER_URL", f"redis://{redis_host}:{str(redis_port)}"
    )
    celery_app.conf.result_backend = os.environ.get(
        "CELERY_RESULT_BACKEND", f"redis://{redis_host}:{str(redis_port)}"
    )
    celery_app.conf.task_track_started = os.environ.get(
        "CELERY_TRACK_STARTED", default=True
    )

    celery_app.conf.worker_send_task_events = True
    celery_app.conf.task_send_sent_event = True

    """
    each block gets its wown queue
    """
    celery_app.conf.task_default_queue = block.name

    """
    set prefetch mult to 1 so that tasks dont get pre-fetched by workers 
    """
    celery_app.conf.worker_prefetch_multiplier = 1

    """
    task messages will be acknowledged after the task has been executed 
    """
    celery_app.conf.task_acks_late = True

    """
    Initiating GPUAllocator only if requires_gpu is True
    """
    if requires_gpu == True:
        gpu_allocator = GPUAllocator(exclude_gpu_ids=exclude_gpu_ids)
    else:
        print(PREFIX + " Initiating server with no GPUs since requires_gpu = False")

    if requires_gpu == True:
        if gpu_allocator.num_gpus < max_num_workers:
            """
            if a task requires a gpu, and the number of workers is > the number of available gpus,
            then max_num_workers is automatically set to the number of gpus available
            this is because eden assumes that each task requires one gpu (all of it)
            """
            warnings.warn(
                "max_num_workers is greater than the number of GPUs found, overriding max_num_workers to be: "
                + str(gpu_allocator.num_gpus)
            )
            max_num_workers = gpu_allocator.num_gpus

    """
    Initiating queue data to keep track of the queue
    """
    queue_data = QueueData(
        redis_port=redis_port, redis_host=redis_host, queue_name=block.name
    )

    """
    Initiate encoder and decoder
    """

    data_encoder = Encoder()
    data_decoder = Decoder()

    """
    Initiate fastAPI app
    """
    app = FastAPI()
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", handle_metrics)

    """
    Initiate result storage on redis
    """

    result_storage = ResultStorage(
        redis_host=redis_host,
        redis_port=redis_port,
    )

    ## set up result storage and data encoder for block
    block.result_storage = result_storage
    block.data_encoder = data_encoder

    """
    initiate a wrapper which handles 4 metrics for prometheus:
    * number of queued jobs
    * number of running jobs
    * number of failed jobs
    * number of succeeded jobs
    """
    prometheus_metrics = PrometheusMetrics()

    """ 
    define celery task
    """

    @celery_app.task(name="run")
    def run(args, token: str):

        ## job moves from queue to running
        prometheus_metrics.queued.dec(1)
        prometheus_metrics.running.inc(1)

        args = data_decoder.decode(args)
        """
        allocating a GPU ID to the tast based on usage
        for now let's settle for max 1 GPU per task :(
        """

        if requires_gpu == True:
            # returns None if there are no gpus available
            gpu_name = gpu_allocator.get_gpu()
        else:
            gpu_name = None  ## default value either if there are no gpus available or requires_gpu = False

        """
        If there are no GPUs available, then it returns a sad message.
        But if there ARE GPUs available, then it starts run()
        """
        if (
            gpu_name == None and requires_gpu == True
        ):  ## making sure there are no gpus available

            status = {
                "status": "No GPUs are available at the moment, please try again later",
            }

        else:

            """
            refer:
            https://github.com/abraham-ai/eden/issues/14
            """
            args = ConfigWrapper(
                data=args,
                token=token,
                result_storage=result_storage,
                gpu=None,  ## will be provided later on in the run
                progress=None,  ## will be provided later on in the run
            )

            if requires_gpu == True:
                args.gpu = gpu_name

            if block.progress == True:
                """
                if progress was set to True on @eden.Block.run() decorator, then add a progress tracker into the config
                """
                args.progress = block.get_progress_bar(
                    token=token, result_storage=result_storage
                )

            try:
                output = block.__run__(args)

                # job moves from running to succeeded
                prometheus_metrics.running.dec(1)
                prometheus_metrics.succeeded.inc(1)

            # prevent further jobs from hitting a busy gpu after a caught exception
            except Exception as e:

                # job moves from running to failed
                prometheus_metrics.running.dec(1)
                prometheus_metrics.failed.inc(1)
                if requires_gpu == True:
                    gpu_allocator.set_as_free(name=gpu_name)
                raise Exception(str(e))

            if requires_gpu == True:
                gpu_allocator.set_as_free(name=gpu_name)

            success = block.write_results(output=output, token=token)

            return success  ## return None because results go to result_storage instead

    @app.post("/run")
    def start_run(config: block.data_model):

        ## job moves into queue
        prometheus_metrics.queued.inc(1)

        """
        refer:
            https://github.com/celery/celery/issues/1813#issuecomment-33142648
        """
        token = generate_random_string(len=10)

        kwargs = dict(args=dict(config), token=token)

        res = run.apply_async(kwargs=kwargs, task_id=token, queue_name=block.name)

        initial_dict = {"config": dict(config), "output": {}, "progress": "__none__"}

        success = result_storage.add(token=token, encoded_results=initial_dict)

        response = {"token": token}

        return response

    @app.post("/update")
    def update(credentials: Credentials, config: block.data_model):

        token = credentials.token
        config = dict(config)

        status = queue_data.get_status(token=token)

        if status["status"] != "invalid token":

            if (
                status["status"] == "queued"
                or status["status"] == "running"
                or status["status"] == "starting"
            ):

                output_from_storage = result_storage.get(token=token)
                output_from_storage["config"] = config

                success = result_storage.add(
                    encoded_results=output_from_storage, token=token
                )

                response = {
                    "status": {
                        "status": "successfully updated config",
                    }
                }

                return response

            elif status["status"] == "failed":

                return {
                    "status": {
                        "status": "could not update config because job failed",
                    }
                }

            elif status["status"] == "complete":

                return {
                    "status": {
                        "status": "could not update config because job is already complete",
                    }
                }

        else:
            response = {"status": {"status": "invalid token"}}
        return response

    @app.post("/fetch")
    def fetch(credentials: Credentials):
        """
        Returns either the status of the task or the result depending on whether it's queued, running, complete or failed.

        Args:
            credentials (Credentials): should contain a token that points to a task
        """

        token = credentials.token

        status = queue_data.get_status(token=token)

        if status["status"] != "invalid token":

            if status["status"] == "running":

                results = result_storage.get(token=token)

                response = {
                    "status": status,
                    "config": results["config"],
                    "output": results["output"],
                }

                if block.progress == True:
                    progress_value = fetch_progress_from_token(
                        result_storage=result_storage, token=token
                    )
                    response["status"]["progress"] = progress_value

            elif status["status"] == "complete":

                results = result_storage.get(token=token)
                    
                ## if results are deleted, it still returns the same schema
                if results == None and remove_result_on_fetch == True:
                    response = {
                        "status": {
                            "status": "removed"
                        },
                    }
                else:
                    response = {
                        "status": status,
                        "config": results["config"],
                        "output": results["output"],
                    }



                if remove_result_on_fetch == True:
                    result_storage.delete(token=token)

            elif (
                status["status"] == "queued"
                or status["status"] == "starting"
                or status["status"] == "failed"
                or status["status"] == "revoked"
            ):

                results = result_storage.get(token=token)

                response = {"status": status, "config": results["config"]}

        else:

            response = {"status": status}  ## invalid token

        return response

    @app.post("/stop")
    async def stop(wait_for: WaitFor):
        """
        Stops the eden block, and exits the script

        Args:
            config (dict, optional): Amount of time in seconds before the server shuts down. Defaults to {'time': 0}.
        """
        logging.info(f"Stopping gracefully in {wait_for.seconds} seconds")
        stop_everything_gracefully(t=wait_for.seconds)

    @app.post("/get_identity")
    def get_identity():
        """
        Returns name and active commit hash of the generator
        """

        repo = git.Repo(search_parent_directories=True)
        name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
        sha = repo.head.object.hexsha

        response = {
            "name": name,
            "commit": sha
        }

        return response


    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "[" + Colors.CYAN + "EDEN" + Colors.END + "] %(asctime)s %(message)s"
    )
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
        "["
        + Colors.CYAN
        + "EDEN"
        + Colors.END
        + "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"
    )

    config = uvicorn.config.Config(app=app, host=host, port=port, log_level=log_level)
    server = ThreadedServer(config=config)

    # context starts fastAPI stuff and run_celery_app starts celery
    with server.run_in_thread():
        message = (
            PREFIX
            + " Initializing celery worker on: "
            + f"redis://localhost:{str(redis_port)}"
        )
        print(message)
        ## starts celery app
        run_celery_app(
            celery_app,
            max_num_workers=max_num_workers,
            loglevel=celery_log_levels[log_level],
            logfile=logfile,
            queue_name=block.name,
        )

    message = PREFIX + " Stopped"

    print(message)

