import uvicorn
from fastapi import FastAPI
from pydantic import create_model

class BaseBlock(object):
    def __init__(self):
        self.__run__ = None
        self.__setup__ = None
        self.default_args = None
        self.data_model = None
    
    def build_pydantic_model(self):
        
        if self.default_args is not None:
            self.data_model = create_model('config', **self.default_args, username = '')
        else:
            raise Exception('default_args are not defined for block.run')

    def setup(self,decorated_fn):

        self.__setup__ = decorated_fn

        def decorator(*args, **kwargs):
            returned_value = decorated_fn(**args, **kwargs)
            return returned_value

        return decorator

    def run(self, args: dict = None):
        
        self.default_args = args
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
