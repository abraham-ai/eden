import time
import unittest
from unittest import TestCase

from eden.client import Client
from eden.datatypes import Image

from eden.datatypes import (
    Image,
)

# misc imports
import PIL
import numpy as np


# misc funtions
def sleep_and_count(t=5, reason=""):
    for i in range(t):
        print(f"{reason} sleeping: {i+1}/{t}")
        time.sleep(1)


def get_keys(d: dict):
    return list(d.keys())


def add_a_task(filename: str):
    c = Client(url="http://localhost:5656", username="test_abraham", verify_ssl=False)

    config = {
        "prompt": "let there be tests",
        "number": 2233,
        "input_image": Image(
            filename
        ),  ## Image() supports jpg, png filenames, np.array or PIL.Image
    }

    run_response = c.run(config)

    return run_response["token"]


class TestSchemas(unittest.TestCase):
    def test_image(self):

        filename = "images/cloud.jpg"
        test_filename = "test_image.jpg"
        pil_image = PIL.Image.open(filename)

        c = Client(
            url="http://127.0.0.1:5656", username="test_abraham", verify_ssl=False
        )

        config = {
            "prompt": "let there be tests",
            "number": 2233,
            "input_image": Image(
                filename
            ),  ## Image() supports jpg, png filenames, np.array or PIL.Image
        }

        run_response = c.run(config)
        """
        expecting:
        {
            'token': some_long_token,
        }
        """
        ideal_keys = ["token"]
        keys_we_got = get_keys(d=run_response)
        self.assertTrue(ideal_keys, keys_we_got)

        token = run_response["token"]

        ## lets spam in a few more task so that we can check queue status
        for i in range(3):
            _ = add_a_task(filename=filename)

        new_token = add_a_task(filename=filename)

        resp = c.fetch(token=new_token)

        """
        expecting:
        {
            'status': {
                'status': queued,
                'queue_position': int
            },
            'config': current_config
        }
        """
        ideal_keys = ["status", "config"]
        keys_we_got = get_keys(d=resp)
        self.assertTrue(ideal_keys, keys_we_got)

        ideal_keys = ["status", "config"]

        if (
            resp["status"]["status"] == "starting"
            or resp["status"]["status"] == "queued"
        ):
            self.assertTrue(ideal_keys == keys_we_got)

        ## waiting for the job to start running
        while True:
            resp = c.fetch(token=new_token)

            sleep_and_count(t=1, reason="waiting for the job to start running... ")
            if (
                resp["status"]["status"] != "queued"
                and resp["status"]["status"] != "starting"
            ):
                break
        """ 
        expected:
        {
            'status': {
                'status': 'running',
                'progress': float

            },
            config: current_config,
            'output': dict
        }
        """
        resp = c.fetch(token=new_token)
        ideal_status = "running"
        print(resp["status"]["status"])
        self.assertTrue(resp["status"]["status"] == ideal_status)
        self.assertTrue(isinstance(resp["output"], dict))
        self.assertTrue(isinstance(resp["status"]["progress"], float))

        while True:
            resp = c.fetch(token=new_token)

            sleep_and_count(t=1, reason="waiting for the job to complete... ")
            if resp["status"]["status"] != "running":
                break

        """
        {
            'status': {
                'status': 'complete'
            },
            'output': dict,
            'config': dict
        }
        """
        resp = c.fetch(token=new_token)

        ## making sure status is complete
        resp = c.fetch(token=new_token)
        ideal_status = "complete"
        self.assertTrue(resp["status"]["status"] == ideal_status)

        ## check returned images in config and output
        resp["config"]["input_image"].save(test_filename)
        self.assertTrue(PIL.Image.open(test_filename), PIL.Image.open(filename))

        ## check returned images in config and output
        resp["output"]["image"].save(test_filename)
        self.assertTrue(PIL.Image.open(test_filename), PIL.Image.open(filename))

        # also check what happens when we send an invalid token
        resp = c.fetch(token="totally not a valid token")
        ideal_status = {"status": "invalid token"}
        self.assertTrue(resp["status"] == ideal_status)


if __name__ == "__main__":
    sleep_and_count(2, reason="waiting for server to start in case it didnt")
    unittest.main()
