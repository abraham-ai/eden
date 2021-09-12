from .progress_tracker import ProgressTracker

from .utils import load_json_as_dict, parse_for_taking_request

class ConfigWrapper(object):
    """ 
    refer: 
    https://github.com/abraham-ai/eden/issues/14
    """
    def __init__(self, data: dict, filename: str, gpu: str, progress: ProgressTracker = None):
        self.data = data
        self.filename = filename
        self.gpu = gpu
        self.progress = progress
        self.__key_to_look_for_in_json_file__ = 'config'

    def __getitem__(self, idx):
        return self.data[idx]

    def refresh(self):
        something_changed = False

        d = parse_for_taking_request(load_json_as_dict(filename= self.filename))
        data = d[self.__key_to_look_for_in_json_file__]
        
        if data != self.data:
            something_changed = True
            self.data = data

        return something_changed



