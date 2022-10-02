"""
Major differences vs original hosting: 
- rabbitmq broker + backend
- no manual interference into rabbitmq
- webhooks to be used for:
    - task queued
    - task status
    - task progress
    - task complete/failed
- a custom enterprise client (?)
"""
import os
import uvicorn


from ..webhook import WebHook
from ..log_utils import Colors
from uvicorn.config import LOGGING_CONFIG
from ..config_wrapper import ConfigWrapper
from ..utils import generate_random_string
from ..threaded_server import ThreadedServer
from ..data_handlers import Encoder, Decoder
from ..log_utils import celery_log_levels, PREFIX




"""
Celery+redis is needed to be able to queue tasks
"""
from celery import Celery
from ..celery_utils import run_celery_app

from fastapi import FastAPI
from ..prometheus_utils import PrometheusMetrics
from fastapi.middleware.cors import CORSMiddleware



from starlette_exporter import PrometheusMiddleware, handle_metrics


def host(
    block,
    webhook_url,
    rabbitmq_broker: str = "amqp://eden:eden@localhost:5672/",
    port=8080,
    host="0.0.0.0",
    max_num_workers=4,
    log_level="warning",
    logfile="logs.log",
):
    """
    things to start:
    - celery app
    - fastapi app
    - init webhook and send a nice message
    """
    webhook = WebHook(url=webhook_url)

    celery_app = Celery(__name__, backend='rpc://', broker=rabbitmq_broker)


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
    initiate a wrapper which handles 4 metrics for prometheus:
    * number of queued jobs
    * number of running jobs
    * number of failed jobs
    * number of succeeded jobs
    """
    prometheus_metrics = PrometheusMetrics()

    data_encoder = Encoder()
    data_decoder = Decoder()


    @celery_app.task(name="run")
    def run(args, token: str):

        ## job moves from queue to running
        prometheus_metrics.queued.dec(1)
        prometheus_metrics.running.inc(1)

        args = data_decoder.decode(args)
        try:
            """
            refer:
            https://github.com/abraham-ai/eden/issues/14
            """
            args = ConfigWrapper(
                data=args,
                token=token,
                result_storage=None,
                gpu=None,  ## will be provided later on in the run
                progress=None,  ## will be provided later on in the run
            )

            if webhook_url is not None:
                webhook(
                    data = {
                        'token': token,
                        'status': 'started'
                    }
                )
            output = block.__run__(args)

            # job moves from running to succeeded
            prometheus_metrics.running.dec(1)
            prometheus_metrics.succeeded.inc(1)


        # prevent further jobs from hitting a busy gpu after a caught exception
        except Exception as e:
            output = None
            # job moves from running to failed
            prometheus_metrics.running.dec(1)
            prometheus_metrics.failed.inc(1)
            raise Exception(str(e))
        
        webhook(
            data = {
                'token': token,
                'status': 'complete'
            }
        )

        return output
    

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

        if webhook_url is not None:
            webhook(
                data = {
                    'token': token,
                    'status': 'queued'
                }
            )

        res = run.apply_async(kwargs=kwargs, task_id=token, queue_name=block.name)

        response = {"token": token}

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
            + " Initializing celery with rabbitmq broker on: "
            + f"{rabbitmq_broker}"
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

