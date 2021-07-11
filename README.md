# Eden


> You were in Eden, the garden of God. Every kind of precious stone adorned you: ruby, topaz, and diamond, beryl, onyx, and jasper, sapphire, turquoise, and emerald. Your mountings and settings were crafted in gold, prepared on the day of your creation. 
> 
> Ezekiel 28:13


Eden is a sandbox for [the Abraham project](http://abraham.ai) to test pipelines for creating generative art with machine learning.


## Setting up a block

Hosting with `eden` requires minimal changes to your existing code. Each unit within `eden` is called a `BaseBlock`, they're the units which take certain inputs and generate art accordingly. 

The first step is to configure `run()`. 

```python 
from eden.block import BaseBlock
from eden.datatypes import Image

eden_block = BaseBlock()
```

> Initiating a `BaseBlock` has 2 optional args. Both args are useful to accept/deny requests based on GPU usage. 
> * `max_gpu_load`: specifies the maximum amount of GPU load, over which `eden` would deny requests.
> * `max_gpu_mem`: specifies the maximum amount of GPU memory that should be allocated, over which `eden` would deny requests.

`run()` is supposed to be the function that runs every time someone wants to use this pipeline to generate art. For now it supports any number of text and images, and numbers as inputs.

```python 
my_args = {
        'prompt': 'hello world', ## text input
        'input_image': Image(),  ## for image input
    }

@eden_block.run(args = my_args)
def do_something(config): 

    # print('doing something for: ', config['username'])
    pil_image = config['input_image']
    device = config['__gpu__']  ## device is something like "cuda:0"

    # do something with your image/text inputs here 

    return {
        'prompt': config['prompt'],  ## returning text
        'image': Image(pil_image)   ## Image() works on PIL.Image, numpy.array and on jpg an png files
    }
```

## Hosting a block

```python
from eden.hosting import host_block

host_block(
    block = eden_block, 
    port= 5656,
    max_num_workers= 4 
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

* If the task is queued, it returns something like `{'status': 'queued', 'waiting_behind': 9}`

* If the task is complete, it returns `{'status': 'complete', 'output': {your_outputs}}`. 

```python
results = c.fetch(token = run_response['token'])
print(results)  
```
