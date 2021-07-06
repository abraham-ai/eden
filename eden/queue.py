from .utils import write_json, load_json_as_dict

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
            'complete': []
        }

        self.__all_tokens__ = []  ## write only

        try: 
            write_json(self.tokens, path = filename)
        except Exception as e:
            raise Exception('Failed to initiate queue on:' + self.filename + '\n' + str(e))

    def update_file(self):
        """
        writes all configs into self.filename
        """
        write_json(dict(self.tokens), path = self.filename)
    

    def join_queue(self, token, config):
        """append into queue

        Args:
            token (str): token
            config (dict): should contain inputs
        """
        self.tokens = load_json_as_dict(self.filename)

        self.tokens['queued'].append(token)
        self.update_file()
        self.__all_tokens__.append(token)

        print(self.tokens['queued'], 'in queue join')

    def set_as_running(self, token):
        """move from queued to running

        Args:
            token (str): token
        """

        # try:
        #     del self.all[token]
        # except KeyError:
        #     import warnings
        #     # raise KeyError(f'Key: {token} not found in keys {self.all.keys()}')
        #     # raise warnings.warn(f'Key: {token} not found in keys {self.all.keys()}')
        #     pass

        self.tokens = load_json_as_dict(self.filename)

        self.tokens['queued'].remove(token)
        self.tokens['running'].append(token)

        self.update_file()


    def set_as_complete(self, token):
        """move from running to complete

        Args:
            token (str): token
        """

        # ## delete from queue
        # del self.all[token]

        self.tokens = load_json_as_dict(self.filename)

        self.tokens['running'].remove(token)
        self.tokens['complete'].append(token)

        self.update_file()

    def get_status_all(self):

        status = {
            'filename': self.filename,
            'length': len(self.tokens),
            'tokens': self.tokens,
        }

        return status

    def get_status(self, token):

        ## if the task has already started
        if token in self.tokens['queued'] and not(token in self.tokens['running'] and token in self.tokens['complete'] ):

            status =  {
                'status': 'queued',
                'waiting_behind': self.tokens['queued'].index(token)
            }
            return status

        elif token in self.tokens['running'] and not(token in self.tokens['queued'] and token in self.tokens['complete']):

            status = {
                'status': 'running',
            }
            return status

        elif token in self.tokens['complete'] and not(token in self.tokens['running'] and token in self.tokens['queued']): 

            status = {
                'status': 'complete',
            }
            return status

        return status

    def clean(self):
        """
        forgets everything except for `self.__all_tokens__`
        """
        # self.all = {}
        self.tokens = {
            'queued': [],
            'running': [],
            'complete': []
        }
        # try: 
        #     write_json(self.tokens, path = self.filename)
        # except Exception as e:
        #     raise Exception('Failed to clean queue on:' + self.filename + '\n' + str(e))


    def check_if_queued(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if token in self.tokens['queued'] else False

    def check_if_running(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if token in self.tokens['running'] else False

    def check_if_complete(self, token):
        self.tokens = load_json_as_dict(self.filename)
        return True if token in self.tokens['complete'] else False

