import requests
from .utils import parse_for_sending_request, parse_response_after_run

class Client(object):
    def __init__(self, url, username = 'client'):
        self.username = username
        self.url = url 

    def run(self, config):
        config['username'] = self.username
        config = parse_for_sending_request(config= config)
        resp = requests.post(self.url + '/run', json=config)
        resp = resp.json()

        resp = parse_response_after_run(resp)
        return resp

    def setup(self):
        resp = requests.get(self.url + '/setup')
        return resp.json()