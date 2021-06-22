import uvicorn
import traceback
from fastapi import FastAPI

from .log_utils import Colors
from uvicorn.config import LOGGING_CONFIG
from .utils import parse_for_taking_request

def host_block(block,  port = 8080):
    app =  FastAPI()

    @app.get('/setup')
    def setup():
        try:
            block.__setup__()
            return {
                'status': 'successful'
            }
        except Exception as e: 
            return {
                'status': 'ERROR: ' + str(e) 
            }

    @app.post('/run')
    def run(args : block.data_model):
        args = dict(args)
        args = parse_for_taking_request(args)
        try:
            output = block.__run__(args)
            return {
                'status': 'success',
                'output': output
            }
        except Exception as e:
            traceback.print_exc()
            return {
                "status": "ERROR : " + str(e) + ". Check Host's logs for full traceback"
            }

    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(asctime)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"
    uvicorn.run(app, port = port)