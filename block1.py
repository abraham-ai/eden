from eden.block import BaseBlock
from eden.hosting import host_block
import time

'''
CLI args for convenience
'''
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num-workers', help='maximum number of workers to be run in parallel',
                    required=False, default=1, type=int)
parser.add_argument('-l', '--logfile', help='filename of log file',
                    required=False, type=str, default=None)
parser.add_argument('-p', '--port', help='localhost port',
                    required=False, type=int, default=5656)
parser.add_argument('-rh', '--redis-host', help='redis host',
                    required=False, type=str, default='localhost')
parser.add_argument('-rp', '--redis-port', help='redis port',
                    required=False, type=int, default=6379)
parser.add_argument('-ug', '--use-gpu', help='set to True if you want to check if eden is on a GPU runtime',
                    required=False, default=False, type=bool)

args = parser.parse_args()


eden_block = BaseBlock()

my_args = {
    'name': 'abraham',
    'number': 12345,
}


@eden_block.run(args=my_args)
def do_something(config):

    device = 'cpu'

    print(f'on device:{device}')

    for i in range(1):
        print(i)
        time.sleep(10)

    return {
        'message': f"hello {config['name']}",
        'number': config['number'],
        'device': device,
        'result': '1'
    }


host_block(
    queue="1",
    block=eden_block,
    port=args.port,
    requires_gpu=args.use_gpu,
    max_num_workers=args.num_workers,
    redis_port=args.redis_port,
    redis_host=args.redis_host,
    logfile=args.logfile  # let us dump logs to stdout
)
