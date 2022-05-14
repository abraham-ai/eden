from redis import Redis
from .utils import dict_to_bytes, bytes_to_dict


class ResultStorage(object):
    def __init__(self, redis_host, redis_port, redis_db=1):
        """Wrapper over redis to fetch and store results.

        Args:
            redis_host (str): url to redis host, generally something like "localhost"
            redis_port (int): port number
            db (int, optional): DB number to look at within redis. Defaults to 1.
        """

        self.redis = self.redis = Redis(
            host=redis_host, port=str(redis_port), db=redis_db
        )

        self.redis.ping()

    def add(self, token, encoded_results: dict):
        """Adds in json-like results into the redis storage.

        Args:
            token (str): unique identifier for each task
            encoded_results (dict): your results encoded using something like: eden.data_handlers.Encoder

        Returns:
            None
        """
        self.redis.set(token, dict_to_bytes(encoded_results))
        return None

    def get(self, token):
        """Tries to fetch results corresponding to a given token from redis
        if there's no such result then it returns None. Also used to obtain intermediate results.

        Args:
            token (str): unique identifier for each task

        Returns:
            dict or None: results from redis
        """

        results = self.redis.get(token)
        if results is not None:
            results = bytes_to_dict(results)
        return results

    def delete(self, token):
        """Deletes a result from redis. Useful when we'll have tons of outputs
        and we won't want to keep them after the user has fetched them

        Args:
            token (str):  unique identifier for each task
        """
        self.redis.delete(token)
