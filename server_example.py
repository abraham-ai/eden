import time
from eden.block import BaseBlock
from eden.datatypes import Image

eden_block = BaseBlock()

my_args = {
        'prompt': 'let there be light', ## text
        'number': 12345,                ## numbers 
        'input_image': Image()          ## images require eden.datatypes.Image()
    }

@eden_block.run(args = my_args, progress = True)
def do_something(config): 

    pil_image = config['input_image']
    some_number = config['number']
    device = config.gpu

    for i in range(5):
        config.refresh()
        config.progress.update(1/10)
        time.sleep(1)

    return {
        'prompt': config['prompt'],  ## returning text
        'number': some_number,       ## returning numbers
        'image': Image(pil_image)    ## Image() works on PIL.Image, numpy.array and on jpg an png files (str)
    }

from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656,
    logfile= 'logs.log',
    log_level= 'info'
)