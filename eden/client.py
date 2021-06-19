import requests

class Client(object):
    def __init__(self, url, username = 'client'):
        self.username = username
        self.url = url 

    def run(self, config):
        config['username'] = self.username
        resp = requests.post(self.url + '/run', json=config)
        return resp.json()

    def setup(self):
        resp = requests.get(self.url + '/setup')
        return resp.json()