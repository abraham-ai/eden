from .progress_tracker import ProgressTracker
from .data_handlers import Encoder, Decoder


class ConfigWrapper(object):
    """
    Wrapper which acts a way to store both the input config got eden.block.Block.__run__()
    and some special components like gpu IDs and progress trackers.

    refer:
    https://github.com/abraham-ai/eden/issues/14

    Args:
        data (dict): input dictionary to be fed into the `eden.block.Block.__run__()` function
        filename (str): filename of the output json file for the current run. Defined as '{results_dir}/{token}.json'
        gpu (str): 'cuda:{x}' where x is the GPU ID provided by `eden.gpu_allocator.GPUAllocator`
        progress (ProgressTracker, optional): If provided, can be used to update the progress of the job. Defaults to None.
        token (str, optional): Unique identifier behind each task run. Defaults to None.
    """

    def __init__(
        self,
        data: dict,
        gpu: str,
        progress: ProgressTracker = None,
        token: str = None,
        result_storage=None,
    ):

        self.data = data
        self.gpu = gpu
        self.progress = progress
        self.token = token

        self.decoder = Decoder()
        self.result_storage = result_storage

        self.__key_to_look_for_in_json_file__ = "config"

    def __getitem__(self, idx):
        """Used to access the input args of the function. Very much like a usual dictionary.

        Args:
            idx (str): key to access a certain value
        """
        return self.data[idx]

    def refresh(self):
        """
        Used to refresh the input args of the function from self.filename.

        Returns:
            bool: True if something changed in the config, else False
        """
        something_changed = False

        d = self.decoder.decode(self.result_storage.get(self.token))

        data = d[self.__key_to_look_for_in_json_file__]

        if data != self.data:
            something_changed = True
            self.data = data

        return something_changed
