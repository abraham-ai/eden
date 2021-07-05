def run_celery_app(app, loglevel = 'INFO', max_num_workers = 1):
    """runs a Celery() instance

    Args:
        app (celery.Celery): celery "app" to be run
        loglevel (str, optional): "INFO" or "DEBUG". Defaults to 'DEBUG'.
    """
    argv = [
        'worker',
        f'--loglevel={loglevel}',
        f'--concurrency={max_num_workers}',
        '-E'
    ]

    print('Running with args: ', argv)
    
    app.worker_main(argv)