from eden.block import BaseBlock
from eden.hosting import host_block

eden_block = BaseBlock()

my_args = {
        'prompt': 'hello world', 
        'number': 12345,               
    }

@eden_block.run(args = my_args)
def do_something(config): 

    some_number = config['number']
    some_text = config['prompt']

    return {
        'prompt': some_text, 
        'number': some_number,       
    }

host_block(
    block = eden_block, 
    port= 5656,
    host = '0.0.0.0',
    logfile= 'logs.log',  ## set to None if you want stdout
    log_level= 'debug',
    max_num_workers= 5,
    requires_gpu= False,
)