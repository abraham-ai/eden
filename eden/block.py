import uvicorn
from fastapi import FastAPI
from pydantic import create_model
from .datatypes import Image
from .progress_tracker import ProgressTracker

class BaseBlock(object):
    """
    Meant to serve as the unit which encapsulates your functions and 
    help host them on a server with multiple GPUs.

    Args:
        max_gpu_load (float, optional): Estimated maximum GPU load that would be required by the job. 0.75 means that it would take up 75% of the load. Defaults to 0.5.
        max_gpu_mem (float, optional): Estimated maximum GPU memory that would be required by the job. 0.75 means that it would take up 75% of the GPU memory. Defaults to 0.5.
    """
    def __init__(self, max_gpu_load = 0.5, max_gpu_mem = 0.5):
        
        self.__run__ = None
        self.__setup__ = None
        self.default_args = None
        self.data_model = None
        self.max_gpu_load = max_gpu_load
        self.max_gpu_mem = max_gpu_mem
        self.progress = False

    def get_progress_bar(self, results_dir, token = None, show_bar = False):
        p = ProgressTracker(token = token, show_bar = show_bar, results_dir = results_dir)
        return p

    def create_default_data_fields(self):
        """
        Creates "skeleton data" for eden's special dataypes found in eden.dataypes. 

        It includes: 
        * eden.datatypes.Image: wraps PIL images, numpy arrays and image files (str)

        """

        for key, value in self.default_args.items():
            if isinstance(value, Image):
                self.default_args[key] = value.__call__()
    
    def build_pydantic_model(self):
        """
        Builds a pydantic model based which tells fastAPI what to expect from a user's requests. 

        Raises:
            Exception when self.default_args are not defined.
        """
         
        if self.default_args is not None:
            self.create_default_data_fields()
            self.data_model = create_model('config', **self.default_args, username = '')
        else:
            raise Exception('default_args are not defined for block.run')

    def run(self, args: dict = None, progress = False):
        """
        Run decorator which defines the function to run on each request from a client. 

        Args:
            args (dict): Specifies the arguments which are to be used in the decorated function. When using special dataypes like images, make sure you use eden.datatypes.Image. 

        Example: 

        ```python 

        my_args = {
            'prompt': 'hello world', ## text input
            'input_image': Image(),  ## for image input
        }

        @eden_block.run(args = my_args)
        def do_something(config): 

            pil_image = config['input_image']
            # do something with your image/text inputs here 

            return {
                'prompt': config['prompt'],  ## returning text
                'image': Image(pil_image)   ## Image() works on PIL.Image, numpy.array and on jpg an png files
            }
        ```
        """
        
        self.default_args = args
        if progress == True: 
            self.progress = True
        self.build_pydantic_model()

        def decorator(fn):
            self.__run__ = fn
            return fn

        return decorator


class BlockBunch(object):
    def __init__(self, blocks):
        self.block_names = list(blocks.keys())
        self.blocks = list(blocks.values())

    def __setup__(self):
        for block in self.blocks:
            block.__setup__()

    def run(self, inputs: dict = {}):
        
        for i in range(len(self.blocks)): 
            self.blocks[i].check_input_types(inputs)
            inputs = self.blocks[i].__run__(inputs)

        return inputs

    def __run__(self, inputs):
        return self.run(inputs)
