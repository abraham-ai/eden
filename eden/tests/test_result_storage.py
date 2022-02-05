import unittest
from unittest import TestCase
from redis import Redis
import redis

from eden.result_storage import ResultStorage
from eden.datatypes import (
    Image,
)


class TestBlock(unittest.TestCase):
    def test_result_storage(self):

        ## first try connecting to 0.0.0.0 (works for local machines) and if that does not work then connect to 172.17.0.1 (gh actions)
        try:
            result_storage = ResultStorage(
                redis_host="0.0.0.0", redis_port=6379, redis_db=0
            )
        except redis.exceptions.ConnectionError:
            result_storage = ResultStorage(
                redis_host="172.17.0.1", redis_port=6379, redis_db=0
            )

        self.assertTrue(isinstance(result_storage.redis, Redis))

        my_args = {
            "prompt": "let there be light",  ## text
            "number": 12345,  ## numbers
            "input_image": Image(
                "images/cloud.jpg"
            ).encode(),  ## force encoding the image here, not done in real usage
        }

        ## add and get stuff from redis
        success = result_storage.add(token="unique_token", encoded_results=my_args)
        output = result_storage.get(token="unique_token")

        self.assertTrue(output == my_args)


if __name__ == "__main__":
    unittest.main()
