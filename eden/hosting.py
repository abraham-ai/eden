import os
import sys
import json
import warnings
import uvicorn
import logging
import threading
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .datatypes import Image
from .queue import QueueData
from .log_utils import Colors
from .models import Credentials
from .config_wrapper import ConfigWrapper
from .threaded_server import ThreadedServer
from .log_utils import log_levels, celery_log_levels, PREFIX

from .utils import (
    parse_for_taking_request, 
    write_json, 
    update_json,
    make_filename_and_token, 
    get_filename_from_token, 
    load_json_as_dict,
    load_json_from_token,
    stop_everything_gracefully
)

from uvicorn.config import LOGGING_CONFIG

'''
Celery+redis is needed to be able to queue tasks
'''
from celery import Celery
from .celery_utils import run_celery_app

'''
tool to allocate gpus on queued tasks
'''
from .gpu_allocator import GPUAllocator

def host_block(block,  port = 8080, results_dir = 'results', max_num_workers = 4, redis_port = 6379, requires_gpu = True, log_level = 'warning', logfile = 'eden_logs.log', exclude_gpu_ids: list = []):
    """
    Use this to host your eden.BaseBlock on a server. Supports multiple GPUs and queues tasks automatically with celery.

    Args:
        block (eden.block.BaseBlock): The eden block you'd want to host. 
        port (int, optional): Localhost port where the block would be hosted. Defaults to 8080.
        results_dir (str, optional): Folder where the results would be stored. Defaults to 'results'.
        max_num_workers (int, optional): Maximum number of tasks to run in parallel. Defaults to 4.
        redis_port (int, optional): Port number for celery's redis server. Make sure you use a non default value when hosting multiple blocks from a single machine. Defaults to 6379.
        requires_gpu (bool, optional): Set this to False if your tasks dont necessarily need GPUs.
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

    '''
    Initiating celery app
    '''
    celery_app = Celery(__name__, broker= f"redis://localhost:{str(redis_port)}")
    celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", f"redis://localhost:{str(redis_port)}")
    celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", f"redis://localhost:{str(redis_port)}")

    """
    Initiating queue data to keep track of the queue
    """
    queue_data = QueueData()

    """
    Initiating GPUAllocator only if requires_gpu is True
    """
    if requires_gpu == True:
        gpu_allocator = GPUAllocator(exclude_gpu_ids= exclude_gpu_ids)
    else:
         print(PREFIX + " Initiating server with no GPUs since requires_gpu = False")
        
    if requires_gpu == True:
        if gpu_allocator.num_gpus < max_num_workers:
            """
            if a task requires a gpu, and the number of workers is > the number of available gpus, 
            then max_num_workers is automatically set to the number of gpus available
            this is because eden assumes that each task requires one gpu (all of it)
            """
            warnings.warn('max_num_workers is greater than the number of GPUs found, overriding max_num_workers to be: '+ str(gpu_allocator.num_gpus))
            max_num_workers = gpu_allocator.num_gpus


    if not os.path.isdir(results_dir):
        print(PREFIX, "Folder: '"+ results_dir+ "' does not exist, running mkdir")
        os.mkdir(results_dir)

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
    
    """ 
    define celery task
    """
    @celery_app.task(name = 'run')
    def run(args, filename:str, token:str):        
        args = parse_for_taking_request(args)
        '''
        allocating a GPU ID to the tast based on usage
        for now let's settle for max 1 GPU per task :(
        '''

        if requires_gpu == True:
            # returns None if there are no gpus available
            gpu_name = gpu_allocator.get_gpu()
        else:
            gpu_name = None  ## default value either if there are no gpus available or requires_gpu = False

        '''
        If there are no GPUs available, then it returns a sad message.
        But if there ARE GPUs available, then it starts run()
        '''
        if gpu_name == None and requires_gpu == True: ## making sure there are no gpus available

            status = {
                'status': 'No GPUs are available at the moment, please try again later',
            }
            queue_data.set_as_running(token = token)
            queue_data.set_as_failed(token = token)

        else:

            """ 
            refer:
            https://github.com/abraham-ai/eden/issues/14
            """
            args = ConfigWrapper(
                data = args,
                filename= get_filename_from_token(token = token, results_dir = results_dir),
                gpu = None,  ## will be provided later on in the run
                progress= None,  ## will be provided later on in the run
                token = token
            )

            if requires_gpu == True:
                args.gpu = gpu_name

            if block.progress == True:
                """
                if progress was set to True on @eden.BaseBlock.run() decorator, then add a progress tracker into the config
                """
                args.progress = block.get_progress_bar(token= token, results_dir = results_dir)

            ## Set token as running in eden.queue.QueueData
            queue_data.set_as_running(token = token)

            ## Set token as running in {results_dir}/{token}.json
            d = load_json_from_token(token = token, results_dir = results_dir)
            d['status'] = {'status': 'running'}
            update_json(dictionary = d, path = filename)
            
            try:
                args.filename = filename
                output = block.__run__(args)
                for key, value in output.items():
                    if isinstance(value, Image):
                        output[key] = value.__call__()

                d = load_json_from_token(token = token, results_dir = results_dir)
                d['output'] = output
                d['status'] = {'status': 'complete'}
                update_json(dictionary = d, path = filename)
                queue_data.set_as_complete(token = token)

                if requires_gpu == True:
                    gpu_allocator.set_as_free(name = gpu_name)

                
            except:
                e =  str(traceback.format_exc( limit= 10))

                ## set task as failed in {results_dir}/{token}.json
                d = load_json_from_token(token = token, results_dir = results_dir)
                d['status'] = {'status': 'failed'}
                d['error'] = e
                update_json(dictionary = d, path = filename)
                
                ## set task as failed in QueueData
                queue_data.set_as_failed(token = token)
                traceback.print_exc()

                if requires_gpu == True:
                    gpu_allocator.set_as_free(name = gpu_name)

                raise


    @app.post('/run')
    def start_run(config: block.data_model):
        
        filename, token = make_filename_and_token(results_dir = results_dir, username = config.username)

        config = dict(config)        
        '''
        write initial results file with config
        '''
        initial_dict = {
            'status': {'status': '__none__'},
            'config': config,
            'output': {}
        }

        write_json(dictionary = initial_dict, path = filename)

        queue_data.join_queue(token = token, config = config)

        run.delay(args = config, filename = filename, token = token)
        status = queue_data.get_status(token = token, results_dir = results_dir)
        
        response = {
            'status': status,
            'token': token
        }

        return response 

    @app.post('/update')
    def update(credentials: Credentials, config: block.data_model):
        
        token = credentials.token
        config = dict(config)

        status = queue_data.get_status(token = token, results_dir = results_dir)

        if status['status'] != 'invalid token':

            if queue_data.check_if_queued(token = token) or queue_data.check_if_running(token = token):

                output_dict = load_json_from_token(token = token, results_dir = results_dir)

                output_dict['config'] = config
                update_json(dictionary  = output_dict, path = get_filename_from_token(results_dir = results_dir, token = token) )
                
                response = {
                    'status': {
                        'status': 'successfully updated config',
                    }
                }

                return response         

            elif queue_data.check_if_failed(token = token):

                return {
                    'status': {
                        'status': 'could not update config because job failed',
                    }
                }

            elif queue_data.check_if_complete(token = token):

                return {
                    'status': {
                        'status': 'could not update config because job is already complete',
                    }
                }

        else:
            response = {
                'status': {
                    'status':'invalid token'
                    }
            }
            return response


    @app.post('/fetch')
    def fetch(credentials: Credentials):
        """        
        Returns either the status of the task or the result depending on whether it's queued, running, complete or failed.

        Args:
            credentials (Credentials): should contain a token that points to a task
        """

        token = credentials.token

        status = queue_data.get_status(token = token, results_dir = results_dir)

        if status['status'] != 'invalid token':

            if queue_data.check_if_queued(token = token):

                output_dict = load_json_from_token(token = token, results_dir = results_dir)

                response = {
                    'status': status,
                    'config': output_dict['config'] ,
                }

                return response

            elif queue_data.check_if_running(token = token):

                try:
                    output_dict = load_json_from_token(token = token, results_dir = results_dir)
                except json.decoder.JSONDecodeError:
                    import time 
                    time.sleep(1e-3)
                    output_dict = load_json_from_token(token = token, results_dir = results_dir)

                response = {
                    'status': status,
                    'config': output_dict['config'] ,
                    'output': output_dict['output'] 
                }

                if block.progress == True:
                    response['status']['progress'] = block.progress_tracker.value

                return response

            elif queue_data.check_if_failed(token = token):

                output_dict = load_json_from_token(token = token, results_dir = results_dir)
                response = {
                    'status': {'status': 'failed'},
                    'config': output_dict['config'] ,
                    'output': output_dict['output'] 
                }

                return response

            elif queue_data.check_if_complete(token = token):

                output_dict = load_json_from_token(token = token, results_dir = results_dir)

                output_dict['status']= {'status': 'complete'}

                return output_dict

        else:
            response = {
                'status': {
                    'status':'invalid token'
                    }
            }
            return response

        
        

    @app.post("/stop")
    async def stop(config:dict):
        """
        Stops the eden block, and exits the script

        Args:
            config (dict, optional): Amount of time in seconds before the server shuts down. Defaults to {'time': 0}.
        """
        logging.info(f'Stopping gracefully in {config["time_to_wait"]} seconds')
        stop_everything_gracefully(t = config['time_to_wait'])
        

    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(asctime)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"

    config = uvicorn.config.Config(app = app, host="0.0.0.0", port=port, log_level= log_level)
    server = ThreadedServer(config = config)

    # context starts fastAPI stuff and run_celery_app starts celery
    with server.run_in_thread():
        message = PREFIX + " Initializing celery worker on: " + f"redis://localhost:{str(redis_port)}"
        print(message)
        ## starts celery app
        run_celery_app(celery_app, max_num_workers=max_num_workers, loglevel= celery_log_levels[log_level], logfile = logfile)

    message = PREFIX + " Stopped"
    print(message)
