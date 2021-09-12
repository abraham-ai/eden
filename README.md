# Eden


> You were in Eden, the garden of God. Every kind of precious stone adorned you: ruby, topaz, and diamond, beryl, onyx, and jasper, sapphire, turquoise, and emerald. Your mountings and settings were crafted in gold, prepared on the day of your creation. 
> 
> Ezekiel 28:13


Eden is a sandbox for [the Abraham project](http://abraham.ai) to deploy pipelines for creating generative art with machine learning.


## Setting up a block

Hosting with `eden` requires minimal changes to your existing code. Each unit within `eden` is called a `BaseBlock`, they're the units which take certain inputs and generate art accordingly. 

The first step is to configure `run()`. 

```python 
from eden.block import BaseBlock
from eden.datatypes import Image

eden_block = BaseBlock()
```

`run()` is supposed to be the function that runs every time someone wants to use this pipeline to generate art. For now it supports text, images, and numbers as inputs.

```python 
my_args = {
        'prompt': 'let there be light', ## text
        'number': 12345,                ## numbers 
        'input_image': Image()          ## images require eden.datatypes.Image()
    }

@eden_block.run(args = my_args, progress = True)
def do_something(config): 

    pil_image = config['input_image']
    some_number = config['number']
    device = config.gpu

    return {
        'text': 'hello',  ## returning text
        'number': some_number,       ## returning numbers
        'image': Image(pil_image)    ## Image() works on PIL.Image, numpy.array and on jpg an png files (str)
    }
```

## Hosting a block

```python
from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656,
    logfile= 'logs.log',  ## set this to None if you dont want one
    log_level= 'info'
)
```

> `max_num_workers` specifies the maximum number of tasks that should be run in parallel at a time.

## Client

A `Client` is the entity that sends requests to a block to generate art. It requires just the `url` to where the client is hosted.

```python
from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')
```

After you start a task with `run()` as shown below, it returns a token as `run_response['token']`. This token should be used later on to check the task status or to obtain your results.

> **Note**: `Image()` is compatible with following types: `PIL.Image`, `numpy.array` and filenames (`str`) ending with `.jpg` or `.png`

```python
config = {
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('test_images/krusty_krab.png')  ## Image() supports jpg, png filenames, np.array or PIL.Image
}

run_response = c.run(config)
```

Fetching results/checking task status using the token can be done using `fetch()`. 

```python
results = c.fetch(token = run_response['token'])
print(results)  
```