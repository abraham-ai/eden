import os 
from .log_utils import Colors
import warnings
from .utils import write_json, load_json_as_dict, get_filename_from_token

class QueueData(object):
    def __init__(self, filename = '__eden_queue__.json'):

        """Example file: 

        {
            "queued": [
                "red_1625591919_s3wxnk1l",
                "blue_1625591919_7ggcllpp",
            ],
            "running": [
                "abraham_1625591919_vecktm1l",
                "pink_1625591919_5tcuhxf9"

            ],
            "complete": [
                "green_1625591919_430tqllh",
                "orange_1625591919_vd8x0kjx",
            ]
        }

        """

        self.filename = filename
       
        self.tokens = {
            'queued': [],
            'running': [],
            'complete': [],
            'failed': []
        }

        self.__all_tokens__ = []  ## write only

        if os.path.exists(self.filename) == False:
            try: 
                write_json(self.tokens, path = filename)
            except Exception as e:
                raise Exception('Failed to initiate queue on:' + self.filename + '\n' + str(e))

        else:
            print("[" + Colors.CYAN+ "EDEN" +Colors.END+ "] " + f'QueueData: File {self.filename} already exists, not making a new file.')


    def update_file(self):
        """
        writes all tokens into `self.filename`
        """
        write_json(dict(self.tokens), path = self.filename)
    

    def join_queue(self, token, config):
        """appends token into queue

        Args:
            token (str): token
            config (dict): should contain inputs
        """
        # self.tokens = load_json_as_dict(self.filename)

        self.tokens['queued'].append(token)
        self.update_file()
        self.__all_tokens__.append(token)

    def set_as_running(self, token):
        """move token from queued to running

        Args:
            token (str): token
        """
        # try:
        #     self.tokens = load_json_as_dict(self.filename)
        # except:
        #     print('COULD NOT LOAD JSON ', self.tokens)

        try:
            self.tokens['queued'].remove(token)
            self.tokens['running'].append(token)

        except: 
            print(self.tokens, 'could not find in queued:', token)
            raise Exception

        self.update_file()


    def set_as_complete(self, token):
        """move token from running to complete

        Args:
            token (str): token
        """

        # self.tokens = load_json_as_dict(self.filename)

        try:
            self.tokens['running'].remove(token)
            self.tokens['complete'].append(token)
        except ValueError:
            print(self.tokens, 'could not find in running:', token)
            raise ValueError

        self.update_file()


    def set_as_failed(self, token):
        """move token from running to failed

        Args:
            token (str): token
        """

        # self.tokens = load_json_as_dict(self.filename)

        self.tokens['running'].remove(token)
        self.tokens['failed'].append(token)

        self.update_file()


    def get_status_all(self):

        status = {
            'filename': self.filename,
            'length': len(self.tokens),
            'tokens': self.tokens
        }

        return status

    def get_status(self, token, results_dir):

        ## if the task has already started
        if token in self.tokens['queued'] and not(token in self.tokens['running'] and token in self.tokens['complete'] ):

            status =  {
                'status': 'queued',
                'waiting_behind': self.tokens['queued'].index(token)
            }
            return status

        elif token in self.tokens['running'] and not(token in self.tokens['queued'] and token in self.tokens['complete']):

            try:
                progress = round(load_json_as_dict(filename= get_filename_from_token(results_dir = results_dir, id = token))['progress'], 3)
            except:                
                warn_message = f"""QueueData.get_status: {get_filename_from_token(results_dir = results_dir, id = token)} is not found, this is probably because you set progress = True on @eden.BaseBlock.run() but did not update progress. 
                If you do not understand whats going on, just set progress = False on @eden.BaseBlock.run()
                """
                warnings.warn(warn_message)
                progress = None

            status = {
                'status': 'running',
                'progress': progress
            }

        elif token in self.tokens['complete'] and not(token in self.tokens['running'] and token in self.tokens['queued']): 
            
            status = {
                'status': 'complete',
            }

        elif token in self.tokens['failed'] and not(token in self.tokens['running'] and token in self.tokens['queued']): 
            
            status = {
                'status': 'failed'
            }

        else:
            
            status = {
                'status': 'unknown'
            }

        return status

    def clean(self):
        """
        forgets everything except for `self.__all_tokens__`
        """
        # self.all = {}
        self.tokens = {
            'queued': [],
            'running': [],
            'complete': [],
            'failed': []
        }

    def check_if_queued(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if token in self.tokens['queued'] else False

    def check_if_running(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if token in self.tokens['running'] else False

    def check_if_complete(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if (token in self.tokens['complete']) else False

    def check_if_failed(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if (token in self.tokens['failed']) else False
