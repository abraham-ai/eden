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
def sleep_and_count(t=5):
    for i in range(t):
        print(f"sleeping: {i+1}/{t}")
        time.sleep(1)


class TestUpdateConfig(unittest.TestCase):
    def test_update_config(self):

        filename = "images/cloud.jpg"
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
        token = run_response["token"]

        sleep_and_count(t=1)

        new_config = {
            "prompt": "updated prompt",
            "number": 3322,
            "input_image": Image(
                filename
            ),  ## Image() supports jpg, png filenames, np.array or PIL.Image
        }
        resp = c.update_config(token=token, config=new_config)

        ## chekcing if config was updated successfully
        ideal_status = "successfully updated config"
        self.assertTrue(resp["status"], ideal_status)

        ## making sure the update config is what its supposed to be
        ideal_config = {
            "prompt": "updated prompt",
            "number": 3322,
            "input_image": pil_image,  ## Image() supports jpg, png filenames, np.array or PIL.Image
        }
        resp = c.fetch(token=token)
        print(resp)
        self.assertTrue(resp["config"], ideal_config)


if __name__ == "__main__":
    sleep_and_count(5)
    unittest.main()
