from .log_utils import PREFIX


def run_celery_app(
    app,
    loglevel="ERROR",
    max_num_workers=4,
    pool="threads",
    logfile=None,
    queue_name="celery",
):
    """
    Runs a Celery() instance.

    Note: `pool = 'threading'` is the only option which did not thrown any CUDA related errors on pytorch.

    To learn more about the args, check:
        https://www.distributedpython.com/2018/10/26/celery-execution-pool/

    Args:
        app (celery.Celery): celery "app" to be run
        loglevel (str, optional): "INFO" or "DEBUG". Defaults to 'DEBUG'.
    """
    argv = [
        "worker",
        f"--loglevel={loglevel}",
        f"--concurrency={max_num_workers}",
        f"--pool={pool}",
        f"--queues={queue_name}",
    ]

    if logfile is not None:
        argv.append(f"--logfile={logfile}")

    print(PREFIX + " Running celery worker with args: ", argv)

    app.worker_main(argv)
