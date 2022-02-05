class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    END = "\033[0m"


log_levels = ["critical", "error", "warning", "info", "debug", "trace"]

PREFIX = "[" + Colors.CYAN + "EDEN" + Colors.END + "]"

celery_log_levels = {}
for level in log_levels:
    celery_log_levels[level] = level.upper()
