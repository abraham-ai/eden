import requests
import json
import time
from .data_handlers import Encoder, Decoder


class Client(object):
    """
    Can be used to send requests to a hosted eden block on some remote (or local) server.

    Args:
        url (str): URL which is printed on your eden block host.
        username (str, optional): Used to identify the client, for now it's only used for debugging. Defaults to 'client'.
        timeout (int, optional): Number of seconds to wait after sending a request before throwing a timeout error. Defaults to 100000.
        verify_ssl (bool, optional): Verify SSL certificate of client URL. Defaults to True
    """

    def __init__(self, url, username="client", timeout=100000, verify_ssl=True):

        self.username = username
        self.url = url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.encoder = Encoder()
        self.decoder = Decoder()

    def get_generator_identity(self):
        """
        Sends a request to the host to get the name and current commit hash of the generator.

        Raises:
            json.decoder.JSONDecodeError: If an invalid json is returned which cannot be decoded.

        Returns:
            dict: {'name': 'name', 'commit': commit_hash}
        """

        resp = requests.post(
            self.url + "/get_identity", timeout=self.timeout, verify=self.verify_ssl
        )

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception("got invalid response from host: \n", str(resp))

        resp = self.decoder.decode(resp)
        return resp

    def run(self, config):
        """
        Sends a request to the host to run a job with the configuration mentioned in config.
        The user might get queued depending on the the number of pending jobs on the host.

        Args:
            config (dict): Dictionary that contains all of the necessary arguments needed to run your task. The keys should be the same as the ones found on `args` in the `@eden.Block.run()` decorator.

        There are 3 main internal steps in this function:
        * `self.encoder.encode()`: Converts `config` to json, ready to be sent to the eden host. Special wrappers found in eden.datatypes help encode special datatypes like images.
        * `requests.post`: sends a request to the hosted block with the json containing your inputs
        * `seld.decoder.decode()`: converts the json received from the request back into a dictionary. If there are any special datatypes like eden.datatypes.Image, they're converted back to more "human" formats like PIL images.

        Raises:
            json.decoder.JSONDecodeError: If an invalid json is returned which cannot be decoded.

        Returns:
            dict: {'status': 'running' or 'queued', 'token': some_long_string}
        """
        config["username"] = self.username
        config = self.encoder.encode(data=config)

        resp = requests.post(
            self.url + "/run", json=config, timeout=self.timeout, verify=self.verify_ssl
        )

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception("got invalid response from host: \n", str(resp))

        resp = self.decoder.decode(resp)
        return resp

    def fetch(self, token):
        """
        Tries to fetch results from the host.
        Returns the output if the task is complete,
        else returns the queue status.
        """
        config = {"token": token}
        resp = requests.post(
            self.url + "/fetch",
            timeout=self.timeout,
            json=config,
            verify=self.verify_ssl,
        )
        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception("got invalid response from host: \n", str(resp))

        resp_keys = list(resp.keys())

        if "output" in resp_keys:
            resp["output"] = self.decoder.decode(resp["output"])
        if "config" in resp_keys:
            resp["config"] = self.decoder.decode(resp["config"])

        return resp

    # still needs to be implemented
    def update_config(self, token, config):
        """
        Update a config by sending request to the host with updated config
        parameters in config_update.
        Returns to the user the same as fetch method.

        Args:
            token (str): token you received after running `some_client.run()
            config_update (dict): Dictionary that contains any config parameters that need to be updated. Non-changed parameters may be omitted.

        Raises:
            json.decoder.JSONDecodeError: If an invalid json is returned which cannot be decoded.

        Returns:
            dict: either {'status': 'complete' 'output': {your_outputs}} or {'status': 'queued', 'waiting_behind': (some int)} or {'status': 'running'}
        """

        config = self.encoder.encode(data=config)

        config = {
            "credentials": {
                "token": token,
            },
            "config": config,
        }

        resp = requests.post(
            self.url + "/update",
            timeout=self.timeout,
            json=config,
            verify=self.verify_ssl,
        )

        try:
            resp = resp.json()
        except json.decoder.JSONDecodeError:
            raise Exception("got invalid response from host: \n", str(resp))

        resp = self.decoder.decode(resp)
        return resp

    def await_results(self, token, fetch_interval=1, show_progress=True):
        """Keeps pinging the server and waits until it has obtained the output/failed the job.

        Args:
            token (str): unique token used to identify the task
            fetch_interval (int, optional): Amount of time in seconds to wait after each /fetch. Defaults to 1.
            show_progress (bool, optional): If set to True, it prints the status and the progress on stdout. Defaults to True.

        Returns:
            dict : output/failure message of the given task
        """

        while True:
            resp = self.fetch(token=token)

            if (
                resp["status"]["status"] == "complete"
                or resp["status"]["status"] == "failed"
            ):
                break
            else:
                if show_progress == True:
                    print(str(resp), end="\r")

            time.sleep(fetch_interval)

        return resp

    def stop_host(self, time=10):
        """
        Stops a running block remotely after `time` seconds.
        """

        config = {"time_to_wait": time}
        try:
            resp = requests.post(
                self.url + "/stop",
                timeout=self.timeout,
                json=config,
                verify=self.verify_ssl,
            )
        except requests.exceptions.ConnectionError:
            """
            This exception is very much expected here since the host would be stopping itself.
            """
            return {"status": {"status": "stopped"}}
