def run_celery_app(app, loglevel = 'INFO', max_num_workers = 4, pool = 'threads'):
    """runs a Celery() instance

    to learn more about the args, check:
    https://www.distributedpython.com/2018/10/26/celery-execution-pool/

    Args:
        app (celery.Celery): celery "app" to be run
        loglevel (str, optional): "INFO" or "DEBUG". Defaults to 'DEBUG'.
    """
    argv = [
        'worker',
        f'--loglevel={loglevel}',
        f'--concurrency={max_num_workers}',
        f'--pool={pool}'
    ]

    print('Running with args: ', argv)
    
    app.worker_main(argv)