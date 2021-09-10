from tqdm import tqdm 
from .utils import (
    get_filename_from_token, 
    load_json_from_token,
    write_json
)


class ProgressTracker():
    def __init__(self, results_dir, token = None):
        self.value = 0.0
        self.token = token
        self.results_dir = results_dir
        self.filename = get_filename_from_token(token = token, results_dir = self.results_dir)

    def update(self, n):

        self.value += n

        d = load_json_from_token(token = self.token, results_dir = self.results_dir)

        d['status']['progress'] = self.value

        write_json(dictionary = d, path = self.filename)