from prometheus_client import Gauge


class PrometheusMetrics:
    """
    wrapper to handle all things prometheus

    Usage:
    ```
    from eden.prometheus_utils import PrometheusMetrics
    pm = PrometheusMetrics()

    pm.queued.set(2)
    pm.running.set(4)
    pm.failed.set(3)
    pm.succeeded.set(5)

    pm.queued.inc(2) ## defaults to 1, can also use dec
    pm.running.inc(4) ## defaults to 1, can also use dec
    pm.failed.inc(3) ## defaults to 1, can also use dec
    pm.succeeded.inc(5) ## defaults to 1, can also use dec
    ```
    """

    def __init__(self):

        self.name_description_mapping = {
            "num_queued_jobs": "number of queued jobs",
            "num_running_jobs": "number of running jobs",
            "num_failed_jobs": "number of failed jobs",
            "num_succeeded_jobs": "number of succeeded jobs",
        }

        self.names = list(self.name_description_mapping.keys())

        """
        refer: https://github.com/prometheus/client_python
        """
        self.queued = Gauge(
            "num_queued_jobs", self.name_description_mapping["num_queued_jobs"]
        )
        self.running = Gauge(
            "num_running_jobs", self.name_description_mapping["num_running_jobs"]
        )
        self.failed = Gauge(
            "num_failed_jobs", self.name_description_mapping["num_failed_jobs"]
        )
        self.succeeded = Gauge(
            "num_succeeded_jobs", self.name_description_mapping["num_succeeded_jobs"]
        )
