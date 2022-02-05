import unittest
from unittest import TestCase

from eden.block import Block
from eden.datatypes import (
    Image,
)


class TestBlock(unittest.TestCase):
    def test_block_init(self):

        eden_block = Block(progress=True, name="some_block_name")

        self.assertTrue(eden_block.__run__ == None)
        self.assertTrue(eden_block.__setup__ == None)
        self.assertTrue(eden_block.default_args == None)
        self.assertTrue(eden_block.data_model == None)
        self.assertTrue(eden_block.progress == True)
        self.assertTrue(eden_block.name == "some_block_name")

    def test_block_build_pydantic_model(self):

        eden_block = Block(progress=True, name="some_block_name")

        my_args = {
            "prompt": "let there be light",  ## text
            "number": 12345,  ## numbers
            "input_image": Image(
                "images/cloud.jpg"
            ),  ## images require eden.datatypes.Image()
        }

        @eden_block.run(args=my_args)
        def do_something(config):

            pil_image = config["input_image"]
            some_number = config["number"]

            return {
                "text": "hello world",  ## returning text
                "number": some_number,  ## returning numbers
                "image": Image(
                    pil_image
                ),  ## Image() works on PIL.Image, numpy.array and on jpg an png files (str)
            }

        pydantic_model = eden_block.data_model()

        self.assertTrue(
            pydantic_model.prompt == my_args["prompt"],
            f"expected {pydantic_model.prompt} to be equal to {my_args['prompt']}",
        )
        self.assertTrue(
            pydantic_model.number == my_args["number"],
            f"expected {pydantic_model.number} to be equal to {my_args['number']}",
        )

        ## add more data types as they come
        self.assertTrue(
            pydantic_model.input_image == my_args["input_image"],
            f"expected {pydantic_model.input_image} to be equal to {my_args['input_image']}",
        )


if __name__ == "__main__":
    unittest.main()
