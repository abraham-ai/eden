def run_celery_app(app, loglevel = 'ERROR', max_num_workers = 4, pool = 'threads', logfile = 'celery_logs.log'):
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
        'worker',
        f'--loglevel={loglevel}',
        f'--concurrency={max_num_workers}',
        f'--pool={pool}',
        f'--logfile={logfile}',
    ]

    print('Running celery worker with args: ', argv)
    
    app.worker_main(argv)