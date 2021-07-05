import os
import json
import uvicorn
import GPUtil
import threading
import traceback
from fastapi import FastAPI

from .log_utils import Colors
from uvicorn.config import LOGGING_CONFIG
from .utils import parse_for_taking_request, write_json, make_filename_and_id, get_filename_from_id, load_json
from .datatypes import Image
from .models import Credentials
from .threaded_server import ThreadedServer

'''
Celery+redis is needed to be able to queue tasks
'''
from celery import Celery
from .celery_utils import run_celery_app

def host_block(block,  port = 8080, results_dir = 'results', max_num_workers = 4):

    '''
    using celery from example: 
    https://testdriven.io/blog/fastapi-and-celery/

    watch this celery worker live with:
    $ celery --broker="redis://localhost:6379" flower --port=6060 
    '''
    celery_app = Celery(__name__)

    celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

    if not os.path.isdir(results_dir):
        print("[" + Colors.CYAN+ "EDEN" +Colors.END+ "]", "Folder: '"+ results_dir+ "' does not exist, running mkdir")
        os.mkdir(results_dir)

    app =  FastAPI()

    @app.get('/setup')
    def setup():
        try:
            block.__setup__()
            return {
                'status': 'complete'
            }
        except Exception as e: 
            return {
                'ERROR': str(e) 
            }


    @celery_app.task(name = 'run')
    def run(args, filename, gpu_id):
        
        args = dict(args)
        args = parse_for_taking_request(args)
        
        args['__gpu__'] = 'cuda:' + str(gpu_id)
        
        try:
            output = block.__run__(args)
            for key, value in output.items():
                if isinstance(value, Image):
                    output[key] = value.__call__()

            write_json(dictionary = output,  path = filename)

        except Exception as e:
            traceback.print_exc()
            return {
                "ERROR" : str(e) + ". Check Host's logs for full traceback"
            }

    @app.post('/run')
    def start_run(args: block.data_model):

        filename, token = make_filename_and_id(results_dir = results_dir, username = args.username)

        '''
        allocating a GPU ID to the tast based on usage
        for now let's settle for max 1 GPU per task :(
        '''
        available_gpu_ids = GPUtil.getAvailable(order = 'first', limit = 1, maxLoad = block.max_gpu_load, maxMemory = block.max_gpu_mem, includeNan=False, excludeID=[], excludeUUID=[])

        '''
        If there are no GPUs available, then it returns a sad message.
        But if there ARE GPUs available, then it starts run()
        '''
        if len(available_gpu_ids) == 0:
            status = {
                'status': 'No GPUs are available at the moment, please try again later',
                'token': token
            }

            return status
        else:
            gpu_id = available_gpu_ids[0]
            run.delay(args = dict(args), filename = filename, gpu_id = gpu_id)

            status = {
                'status': 'started',
                'token': token
            }

            write_json(
                dictionary = status,  
                path = filename
            )

        return status 

    @app.post('/fetch')
    def fetch(credentials: Credentials):

        token = credentials.token
        file_path = get_filename_from_id(results_dir = results_dir, id = token)

        if os.path.exists(file_path):
            results = load_json(file_path)

            if results != {'status': 'started','token': token}:
                return {
                    'status': 'completed',
                    'output': results 
                }
            else:
                return {
                    'status': 'running',
                }

        else:
            return {
                'ERROR': 'invalid token: ' + token
            }

    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(asctime)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"


    config = uvicorn.config.Config(app = app, port=port)
    server = ThreadedServer(config = config)

    ## context starts fastAPI stuff
    with server.run_in_thread():
        message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "]" + " Initializing celery worker on: " + "redis://localhost:6379"
        print(message)
        ## starts celery app
        run_celery_app(celery_app, max_num_workers=max_num_workers)

    message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "]" + " Stopped"
    print(message)
