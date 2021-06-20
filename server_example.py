from eden.block import BaseBlock
from eden.datatypes import Image

eden_block = BaseBlock()

@eden_block.setup
def some_setup():
    pass  ## your setup goes here

my_args = {
        'prompt': 'hello world', ## text input
        'input_image': Image(),  ## for image input
    }

@eden_block.run(args = my_args)
def do_something(config): 

    # print('doing something for: ', config['username'])
    pil_image = config['input_image']
    # do something with your image/text inputs here 

    return {
        'prompt': config['prompt'],  ## returning text
        'image': Image(pil_image)   ## Image() works on PIL.Image, numpy.array and on jpg an png files
    }

from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656
)