from eden.block import BaseBlock
from eden.hosting import host_block
from eden.image_utils import encode, decode

my_block = BaseBlock()

@my_block.setup
def some_setup():
    pass
    # print('setup complete')

@my_block.run(
    args = {
        'prompt': 'hello world', ## default args
        'input_image': '',       ## leaving this empty works too
    }
)
def do_something(config): 

    print('doing something for: ', config['username'])
    pil_image = decode(config['input_image'])

    # do something with your image/text inputs here 

    return {
        'prompt': config['prompt'],
        'image': encode(pil_image)
    }

if __name__ == '__main__':

    host_block(
        block = my_block, 
        port= 5656
    )