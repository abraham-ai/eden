from tqdm import tqdm 
from .utils import write_json, get_filename_from_token


class ProgressTracker():
    def __init__(self, results_dir, token = None, show_bar = False):
        self.value = 0.0
        self.max = 1.0
        self.token = token
        self.results_dir = results_dir
        self.filename = get_filename_from_token(results_dir = self.results_dir, id = self.token)

        if show_bar == True:
            if token is None:
                self.bar = tqdm(desc = 'Running: ', initial= 0, total= 1, mininterval= 1e-5)
            else:
                self.bar = tqdm(desc = f'Running for {token} : ', initial= 0, total= 1, mininterval= 1e-5)

        else: 
            self.bar = None

    def update(self, n):
        if self.bar is not None:
            self.bar.update(n)
        self.value += n

        status = {
            'progress': self.value
        }

        write_json(dictionary = status, path = self.filename)