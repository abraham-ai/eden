import requests
import json
import time
from .utils import parse_for_sending_request, parse_response_after_run

class Client(object):
    """
    Can be used to send requests to a hosted eden block on some remote (or local) server. 

    Args:
        url (str): URL which is printed on your eden block host.
        username (str, optional): Used to identify the client, for now it's only used for debugging. Defaults to 'client'.
        timeout (int, optional): Number of seconds to wait after sending a request before throwing a timeout error. Defaults to 100000.
        verify_ssl (bool, optional): Verify SSL certificate of client URL. Defaults to True
    """
    def __init__(self, url, username = 'client', timeout = 100000, verify_ssl = True):
        
        self.username = username
        self.url = url 
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def run(self, config):
        """
        Sends a request to the host to run a job with the configuration mentioned in config. 
        The user might get queued depending on the the number of pending jobs on the host.

        Args:
            config (dict): Dictionary that contains all of the necessary arguments needed to run your task. The keys should be the same as the ones found on `args` in the `@eden.BaseBlock.run()` decorator.

        There are 3 main internal steps in this function: 
        * `parse_for_sending_request`: Converts `config` to json, ready to be sent to the eden host. Special wrappers found in eden.datatypes help encode special datatypes like images. 
        * `requests.post`: sends a request to the hosted block with the json containing your inputs
        * `parse_response_after_run`: converts the json received from the request back into a dictionary. If there are any special datatypes like eden.datatypes.Image, they're converted back to more "human" formats like PIL images.

        Raises:
            json.decoder.JSONDecodeError: If an invalid json is returned which cannot be decoded.

        Returns:
            dict: {'status': 'running' or 'queued', 'token': some_long_string}
        """
        config['username'] = self.username
        config = parse_for_sending_request(config= config)
        resp = requests.post(self.url + '/run', json=config, timeout = self.timeout, verify = self.verify_ssl)

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception('got invalid response from host: \n', str(resp))
            
        try:
            resp = parse_response_after_run(resp)
            return resp
        except KeyError:
            return resp


    def fetch(self, token):
        """
        Tries to fetch results from the host. Returns the output if the task is complete, else returns the queue status.

        Args:
            token (str): token you received after running `some_client.run()`

        Raises:
            json.decoder.JSONDecodeError: If an invalid json is returned which cannot be decoded.

        Returns:
            dict: either {'status': 'complete' 'output': {your_outputs}} or {'status': 'queued', 'waiting_behind': (some int)} or {'status': 'running'}
        
        """
        config = {
            'token': token
        }
        resp = requests.post(self.url + '/fetch', timeout = self.timeout, json = config, verify = self.verify_ssl)

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception('got invalid response from host: \n', str(resp))
            
        resp = parse_response_after_run(resp)
        return resp

    def await_results(self, token, fetch_interval = 1, show_progress = True):

        while True:
            resp = self.fetch(token = token)

            if resp['status'] == 'complete':
                break
            else:
                if show_progress == True:
                    print(str(resp), end = '\r')

            time.sleep(fetch_interval)

        return resp

