from eden.block import Block
from eden.datatypes import Image, Video
from eden.hosting import host_block

eden_block = Block()

my_args = {
    "input_image": Image(),  ## images require eden.datatypes.Image()
    "input_video": Video(),  ## images require eden.datatypes.Video()
}


@eden_block.run(args=my_args, progress=False)
def do_something(config):

    # todo: maybe process the video frame by frame
    output_image = config["input_image"]
    output_video = config["input_video"]

    return {"output_video": output_video }


host_block(
    block=eden_block,
    port=5656,
    logfile="logs.log",
    log_level="debug",
    redis_host="eden-dev-gene-redis",
    max_num_workers=4,
    requires_gpu=True,
)
