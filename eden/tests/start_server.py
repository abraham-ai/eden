import threading

from eden.hosting import host_block
from eden.tests.server import eden_block

def run_server():
    host_block(
        block = eden_block, 
        port= 5656,
        logfile= None,
        log_level= 'info',
        requires_gpu= False,
        max_num_workers= 3
    )

def run_server_in_another_thread():
    t = threading.Thread(target= run_server)
    t.start()

if __name__ == '__main__':
    print('here')
    run_server_in_another_thread()
    print('started server')
