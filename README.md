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
from eden.datatypes import Image

eden_block = BaseBlock()

@eden_block.setup
def some_setup():
    pass  ## your setup goes here
```

`run()` is supposed to be the function that runs every time someone wants to use this pipeline to generate art. For now it supports any number of text and image inputs.

```python 
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
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

setup_response = c.setup()
```

After you start a task as shown below, it returns a token as `run_response['token']`. This token should be used later on to check the task status or to obtain results.

> **Note**: `Image()` is compatible with following types: `PIL.Image`, `numpy.array` and filenames (`str`) ending with `.jpg` or `.png`

```python
config = {
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('test_images/krusty_krab.png')  ## Image() supports jpg, png filenames, np.array or PIL.Image
}

run_response = c.run(config)
```

Fetching results/checking task status using the token can be done using `fetch()`. If the task is complete, it returns `{'status': 'complete', 'output': {your_outputs}}`. If it's not complete, it returns `{'status': 'running'}`

```python
results = c.fetch(token = run_response['token'])
print(results)  
```
