import os
import time
import json
import secrets, string


def generate_random_string(len):
    x = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for i in range(len)
    )
    return x


def dict_to_bytes(dictionary: dict):

    dict_in_bytes = json.dumps(dictionary).encode("utf-8")
    return dict_in_bytes


def bytes_to_dict(dict_in_bytes):
    dict_str = dict_in_bytes.decode("UTF-8")
    dict_from_str = json.loads(dict_str)
    return dict_from_str


def stop_everything_gracefully(t):
    time.sleep(t)
    os._exit(0)
