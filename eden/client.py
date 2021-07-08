import requests
import json
from .utils import parse_for_sending_request, parse_response_after_run

class Client(object):
    def __init__(self, url, username = 'client', timeout = 100000):
        self.username = username
        self.url = url 
        self.timeout = timeout

    def run(self, config):
        config['username'] = self.username
        config = parse_for_sending_request(config= config)
        resp = requests.post(self.url + '/run', json=config, timeout = self.timeout)

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception('got invalid response from host: \n', str(resp))
            
        try:
            resp = parse_response_after_run(resp)
            return resp
        except KeyError:
            return resp

    def setup(self):
        resp = requests.get(self.url + '/setup', timeout = self.timeout)
        return resp.json()

    def fetch(self, token):
        config = {
            'token': token
        }
        resp = requests.post(self.url + '/fetch', timeout = self.timeout, json = config)

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception('got invalid response from host: \n', str(resp))
            
        resp = parse_response_after_run(resp)
        return resp

