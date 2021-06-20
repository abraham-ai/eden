# Eden


> You were in Eden, the garden of God. Every kind of precious stone adorned you: ruby, topaz, and diamond, beryl, onyx, and jasper, sapphire, turquoise, and emerald. Your mountings and settings were crafted in gold, prepared on the day of your creation. 
> 
> Ezekiel 28:13


Eden is a sandbox for [the Abraham project](http://abraham.ai) to test pipelines for creating generative art with machine learning.


## Hosting

Hosting with `eden` requires minimal changes to your existing code. Each unit within `eden` is called a `BaseBlock`, they're the units which take certain inputs and generate art accordingly. 

The first step is to configure `setup()` and `run()`. 

```python 
from eden.block import BaseBlock
from eden.image_utils import encode, decode

eden_block = BaseBlock()

@eden_block.setup
def some_setup():
    pass  ## your setup goes here
```

`run()` is supposed to be the function that runs every time someone wants to use this pipeline to generate art. For now it supports any number of text and image inputs.

> **Note:** `decode()` is compatible with `Base64` encoded bytes-like object or ASCII strings. It's meant to work with `encode()`. 

```python 
my_args = {
        'prompt': 'hello world', ## text input
        'input_image': '',       ## for image input, it can be left empty
    }

@eden_block.run(args = my_args)
def do_something(config): 

    pil_image = decode(config['input_image'])
    # do something with your image/text inputs here 

    return {
        'prompt': config['prompt'],  ## returning text
        'image': encode(pil_image)   ## encode() works on PIL.Image, numpy.array and on jpg an png files
    }
```

Running on localhost

```python
from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656
)
```

## Client

A `Client` is the entity that sends requests to a block to generate art. It requires just the `url` to where the client is hosted. If you're using images as input, use `encode()` to encode it before sending a request. 

```python
from eden.client import Client
from eden.image_utils import decode, encode

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham') ## username is optional

setup_response = c.setup()
```

Fetching results and saving images

> **Note**: `encode()` is compatible with following types: `PIL.Image`, `numpy.array` and filenames (`str`) ending with `.jpg` or `.png`

```python
config = {
    'prompt': 'let there be light',  ## sample text input
    'input_image': encode('test_images/krusty_krab.png')  ## encode() supports jpg, png files, np.array or PIL.Image
}

run_response = c.run(config)

# convert back to PIL and save the image
pil_image = decode(run_response['output']['image'])
pil_image.save('from_server.png')
```
