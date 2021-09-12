from .progress_tracker import ProgressTracker

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

