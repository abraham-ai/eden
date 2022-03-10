from eden.block import Block
from eden.hosting import host_block
from eden.datatypes import Image

# creating fake delays
import time

# creating fake images
import numpy as np

eden_block = Block()

my_args = {
    "width": 224,  ## width
    "height": 224,  ## height
    "input_image": Image(),  ## images require eden.datatypes.Image()
}


@eden_block.run(args=my_args, progress=False)
def do_something(config):

    pil_image = config["input_image"]
    num_steps = 10

    for i in range(num_steps):
        time.sleep(0.5)
        config.progress.update(1 / num_steps)

        ## different width and height on each iter
        width, height = int(config["width"] / (i + 1)), int(config["height"] / (i + 1))
        intermediate_image = (np.random.rand(width, height, 3) * 255).astype(np.uint8)

        intermediate_results = {
            "intermediate_creation": Image(intermediate_image),
            "width": width,
            "height": height,
        }

        ## write intermediate results
        eden_block.write_results(output=intermediate_results, token=config.token)

    return {
        "creation": Image(pil_image),
        "width": width,
        "height": height,
    }


host_block(
    block=eden_block,
    port=5656,
    host="0.0.0.0",
    logfile="logs.log",  ## set to None if you want stdout
    log_level="debug",
    max_num_workers=5,
    requires_gpu=False,
)
