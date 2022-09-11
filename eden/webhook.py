from argparse import ONE_OR_MORE
from base64 import encode
import json
import requests

from typing import Callable

class WebHook:
    def __init__(self, url: str, encode_fn : Callable = None) -> None:
        self.url = url
        self.encode_fn = encode_fn

    def __call__(self, data: dict):
        if self.encode_fn is not None:
            data = self.encode_fn(data)
        r = requests.post(self.url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        return r