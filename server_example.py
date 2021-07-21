from eden.block import BaseBlock
from eden.datatypes import Image

eden_block = BaseBlock()

my_args = {
        'prompt': 'let there be light', ## text
        'number': 12345,                ## numbers 
        'input_image': Image()          ## image requires Image()
    }

@eden_block.run(args = my_args, progress = True)
def do_something(config): 

    pil_image = config['input_image']
    some_number = config['number']
    device = config['__gpu__']

    # do something with your inputs here 

    for i in range(10):
        config['__progress__'].update(1/10)

    raise KeyError

    return {
        'prompt': config['prompt'],  ## returning text
        'number': some_number,       ## returning numbers
        'image': Image(pil_image)    ## Image() works on PIL.Image, numpy.array and on jpg an png files
    }

from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656,
    log_level= 'warning' ## options : 'critical', 'error', 'warning', 'info', 'debug', 'trace'
)