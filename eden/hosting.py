import uvicorn
from fastapi import FastAPI
from .log_utils import Colors
from uvicorn.config import LOGGING_CONFIG

def host_block(block,  port = 8080):
    app =  FastAPI()

    @app.get('/setup')
    def setup():
        try:
            block.__setup__()
            return {
                'setup': 'setup complete!'
            }
        except Exception as e: 
            return {
                'ERROR': str(e) 
            }

    @app.post('/run')
    def run(args : block.data_model):
        try:            
            output = block.__run__(dict(args))
            return {
                'run': 'run successful',
                'output': output
            }
        except Exception as e: 
            return {
                'ERROR': str(e) 
            }

    ## overriding the boring old [INFO] thingy
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(asctime)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] %(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s"
    uvicorn.run(app, port = port)