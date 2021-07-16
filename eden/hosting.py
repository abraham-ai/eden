import os
import json
import uvicorn
import GPUtil
import threading
import traceback
from fastapi import FastAPI

from .log_utils import Colors
from uvicorn.config import LOGGING_CONFIG
from .utils import parse_for_taking_request, write_json, make_filename_and_token, get_filename_from_token, load_json_as_dict
from .datatypes import Image
from .models import Credentials
from .threaded_server import ThreadedServer
from .queue import QueueData

'''
Celery+redis is needed to be able to queue tasks
'''
from celery import Celery
from .celery_utils import run_celery_app

def host_block(block,  port = 8080, results_dir = 'results', max_num_workers = 4, redis_port = 6379):
    """
    Use this to host your eden.BaseBlock on a server. Supports multiple GPUs and queues tasks automatically with celery.

    Args:
        block (eden.block.BaseBlock): The eden block you'd want to host. 
        port (int, optional): Localhost port where the block would be hosted. Defaults to 8080.
        results_dir (str, optional): Folder where the results would be stored. Defaults to 'results'.
        max_num_workers (int, optional): MAximum number of tasks to run in parallel. Defaults to 4.
        redis_port (int, optional): Port number for celery's redis server. Make sure you use a non default value when hosting multiple blocks from a single machine. Defaults to 6379.
    """

    '''
    watch this celery worker live with:
    $ celery --broker="redis://localhost:6379" flower --port=6060 
    '''
    celery_app = Celery(__name__, broker= f"redis://localhost:{str(redis_port)}")

    celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", f"redis://localhost:{str(redis_port)}")
    celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", f"redis://localhost:{str(redis_port)}")

    queue_data = QueueData()

    if not os.path.isdir(results_dir):
        print("[" + Colors.CYAN+ "EDEN" +Colors.END+ "]", "Folder: '"+ results_dir+ "' does not exist, running mkdir")
        os.mkdir(results_dir)

    app =  FastAPI()

    @celery_app.task(name = 'run')
    def run(args, filename, token):
        
        args = dict(args)
        args = parse_for_taking_request(args)

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
            }

        else:

            args['__gpu__'] = 'cuda:' + str(available_gpu_ids[0])

            if block.progress == True:
                args['__progress__'] = block.get_progress_bar(token= token,  results_dir = results_dir)

            queue_data.set_as_running(token = token)
            
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

            queue_data.set_as_complete(token = token)

    @app.post('/run')
    def start_run(args: block.data_model):
        
        filename, token = make_filename_and_token(results_dir = results_dir, username = args.username)

        args = dict(args)
        queue_data.join_queue(token = token, config = args)

        run.delay(args = args, filename = filename, token = token)
        status = queue_data.get_status(token = token, results_dir = results_dir)
        status['token']  = token

        return status 

    @app.post('/fetch')
    def fetch(credentials: Credentials):

        token = credentials.token

        if queue_data.check_if_queued(token = token) or queue_data.check_if_running(token = token):

            status = queue_data.get_status(token = token, results_dir = results_dir)

            return status

        elif queue_data.check_if_complete(token = token):
            file_path = get_filename_from_token(results_dir = results_dir, id = token)
            results = load_json_as_dict(file_path)

            status = {
                'status': 'complete',
                'output': results
            }

            return status

    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(asctime)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"

    config = uvicorn.config.Config(app = app, port=port)
    server = ThreadedServer(config = config)

    # context starts fastAPI stuff and run_celery_app starts celery
    with server.run_in_thread():
        message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "]" + " Initializing celery worker on: " + "redis://localhost:6379"
        print(message)
        ## starts celery app
        run_celery_app(celery_app, max_num_workers=max_num_workers)

    message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "]" + " Stopped"
    print(message)
