import contextlib
import time
import threading
import uvicorn


class ThreadedServer(uvicorn.Server):
    """
    A neat way to run a uvicorn server in a new thread
    Refer issue:
        https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
    """

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
