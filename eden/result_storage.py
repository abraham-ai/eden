from redis import Redis
from .utils import dict_to_bytes, bytes_to_dict

class ResultStorage(object): 
    def __init__(self, redis_host, redis_port, db = 1): 
        """Wrapper over redis to fetch and store results.

        Args:
            redis_host (str): url to redis host, generally something like "localhost"
            redis_port (int): port number
            db (int, optional): DB number to look at within redis. Defaults to 1.
        """

        self.redis = self.redis = Redis(
            host= redis_host,
            port= str(redis_port),
            db = db
        )

    def add(self, token, encoded_results: dict):

        success = True

        # try:
        self.redis.set(
            token,
            dict_to_bytes(encoded_results)
        )
        # except: 
        #     success = False

        return success

    def get(self, token):

        results = self.redis.get(token)
        if results is not None:
            results = bytes_to_dict(results)
        return results