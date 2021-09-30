import os 
import json
from .log_utils import Colors
import warnings
from .utils import write_json, load_json_as_dict, get_filename_from_token

class QueueData(object):
    """
    Simple way to keep a track of the tasks done on multiple threads. 

    Args:
        filename (str): name of the json file where the data is stored. Defaults to: "__eden_queue__.json"
    """
    def __init__(self, filename = '__eden_queue__.json'):

        self.data = {}
        self.filename = filename

        self.queue = []  ## i

        self.name_mapping = {
            'PENDING': 'queued',
            'STARTED': 'running',
            'SUCCESS': 'complete',
            'FAILURE': 'failed'
        }

    def get_status(self, token):

        try:
            status = self.name_mapping[self.data[token].status]

            status_to_return = {
                'status': status,
            }

            if status == 'queued':
                queue_pos = self.get_queue_position(token = token)
                status_to_return['queue_position'] = queue_pos

        except KeyError:
            
            status_to_return = {
                'status': 'invalid token'
            }

        return status_to_return

    def __getitem__(self, idx):
        return self.data[idx]

    def get_all(self):
        
        d = {}

        for key in self.data.keys():
            d[key]= self.name_mapping[self.data[key].status]

        return d

    def add_to_queue(self, token, res):
        self.data[token] = res
        self.queue.append(token)
        
    def set_as_running(self, token):
        self.queue.remove(token)


    def get_queue_position(self, token):
        return self.queue.index(token)