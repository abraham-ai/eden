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


class TestDataTypes(unittest.TestCase):
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
        token = run_response["token"]

        sleep_and_count(t=8)

        resp = c.fetch(token=token)

        ## check status
        ideal_status = {"status": "complete"}
        print(resp["status"])
        self.assertTrue(resp["status"] == ideal_status, msg=f"got {resp['status']}")

        ## save returned image
        resp["config"]["input_image"].save(test_filename)

        ## check if theyre the same
        self.assertTrue(PIL.Image.open(test_filename), PIL.Image.open(filename))


if __name__ == "__main__":
    unittest.main()
