from eden.block import Block
from eden.datatypes import Image

from eden.hosting import host_block
import time

## set this to true if you want to run tests on gpus
REQUIRES_GPU = False

eden_block = Block(name="eden_block")

my_args = {
    "prompt": "let there be tests",  ## text
    "number": 12345,  ## numbers
    "input_image": Image(),  ## image requires Image()
}


@eden_block.run(args=my_args, progress=True)
def do_something(config):

    pil_image = config["input_image"]
    some_number = config["number"]

    print(f"running job for: {config.token}")

    if REQUIRES_GPU:
        device = config.gpu

    for i in range(5):

        config.refresh()
        config.progress.update(1 / 5)
        time.sleep(1)

    return {
        "prompt": "test message",  ## returning text
        "number": some_number,  ## returning numbers
        "image": Image(
            pil_image
        ),  ## Image() works on PIL.Image, numpy.array and on jpg an png files
    }
