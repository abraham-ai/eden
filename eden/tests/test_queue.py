import time
import unittest
from redis import Redis
import redis
from unittest import TestCase

from eden.queue import QueueData
from eden.client import Client
from eden.result_storage import ResultStorage

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


class TestQueue(unittest.TestCase):
    def test_queue(self):

        filename = "images/cloud.jpg"

        try:
            queue_data = QueueData(
                redis_host="0.0.0.0",
                redis_port=6379,
                redis_db=0,
                queue_name="eden_block",
            )
        except redis.exceptions.ConnectionError:
            queue_data = QueueData(
                redis_host="172.17.0.1",
                redis_port=6379,
                redis_db=0,
                queue_name="eden_block",
            )

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

        self.assertTrue(isinstance(queue_data.redis, Redis))

        tokens = []

        for i in range(3):
            token = c.run(config)["token"]
            tokens.append(token)

        tokens_in_queue = queue_data.get_queue()
        print(tokens_in_queue)

        self.assertTrue(type(tokens_in_queue) == list)

        if len(tokens_in_queue) > 0:
            for i in range(len(tokens_in_queue)):
                self.assertTrue(type(tokens_in_queue[i]) == str)

        sleep_and_count(1)
        tokens_in_queue = queue_data.get_queue()
        for t in tokens:
            resp = queue_data.get_status(token=t)
            self.assertTrue(type(resp) == dict)
            self.assertTrue("status" in list(resp.keys()))


if __name__ == "__main__":
    unittest.main()
