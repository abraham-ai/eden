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

    ## file whose contents get updated when the client calls: Client.update_config()
    config_filename = config['__filename__']

    for i in range(10):

        ## this is the stuff you need to read the updated config on the fly
        from eden.utils import load_json_as_dict, parse_for_taking_request
        new_config = parse_for_taking_request(load_json_as_dict(config_filename))


        import logging
        logging.info(new_config) ### this is just to write it into the logs for debugging

        config['__progress__'].update(1/10)

        import time
        time.sleep(1)

    return {
        'prompt': config['prompt'],  ## returning text
        'number': some_number,       ## returning numbers
        'image': Image(pil_image)    ## Image() works on PIL.Image, numpy.array and on jpg an png files
    }

from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656,
    logfile= 'eden_logs.log',
    log_level= 'info'
)