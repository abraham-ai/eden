from tqdm import tqdm
from .result_storage import ResultStorage


class ProgressTracker:
    def __init__(self, token: str, result_storage: ResultStorage):
        self.value = 0.0
        self.token = token
        self.result_storage = result_storage

    def update(self, n):

        self.value += n

        output_from_storage = self.result_storage.get(token=self.token)
        output_from_storage["progress"] = self.value

        success = self.result_storage.add(
            encoded_results=output_from_storage, token=self.token
        )

        return success


def fetch_progress_from_token(result_storage: ResultStorage, token: str):
    progress_value = result_storage.get(token=token)["progress"]
    return progress_value
