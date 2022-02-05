import argparse
import threading
from pprint import pprint
from eden.hosting import host_block
from eden.tests.server import eden_block

parser = argparse.ArgumentParser()

parser.add_argument(
    "-p", "--port", help="localhost port", required=False, type=int, default=5656
)
parser.add_argument(
    "-l",
    "--logfile",
    help="filename of log file",
    required=False,
    type=str,
    default=None,
)
parser.add_argument(
    "-ll", "--log-level", help="log level", required=False, type=str, default="info"
)
parser.add_argument(
    "-rg",
    "--requires-gpu",
    help="set to True if you want to check if eden is on a GPU runtime",
    required=False,
    default=False,
    type=bool,
)
parser.add_argument(
    "-mnw",
    "--max-num-workers",
    help="maximum number of workers to be run in parallel",
    required=False,
    default=1,
    type=int,
)
parser.add_argument(
    "-ho", "--host", help="host name", required=False, default="0.0.0.0", type=str
)

## migh also need '172.17.0.1'
parser.add_argument(
    "-rh",
    "--redis-host",
    help="redis host name",
    required=False,
    default="localhost",
    type=str,
)
parser.add_argument(
    "-rp", "--redis-port", help="redis port", required=False, type=int, default=6379
)

args = parser.parse_args()


def run_server(
    port: int,
    logfile: str,
    log_level: str,
    requires_gpu: bool,
    max_num_workers: int,
    host: str,
    redis_host: str,
    redis_port: int,
):
    host_block(
        block=eden_block,
        port=port,
        logfile=logfile,
        log_level=log_level,
        requires_gpu=requires_gpu,
        max_num_workers=max_num_workers,
        host=host,
        redis_host=redis_host,  ## use 'localhost' if you're running tests locally on a machine
    )


def run_server_in_another_thread(kwargs):
    t = threading.Thread(target=run_server, kwargs=kwargs)
    t.start()


if __name__ == "__main__":

    kwargs = {
        "port": args.port,
        "logfile": args.logfile,
        "log_level": args.log_level,
        "requires_gpu": args.requires_gpu,
        "max_num_workers": args.max_num_workers,
        "host": args.host,
        "redis_host": args.redis_host,
        "redis_port": args.redis_port,
    }

    run_server_in_another_thread(kwargs=kwargs)
    print("\nStarted test server with kwargs:")
    pprint(kwargs)
