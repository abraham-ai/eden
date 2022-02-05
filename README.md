# Eden

[![tests](https://github.com/abraham-ai/eden/actions/workflows/main.yml/badge.svg)](https://github.com/abraham-ai/eden/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/abraham-ai/eden/branch/master/graph/badge.svg?token=83QZRAE4XS)](https://codecov.io/gh/abraham-ai/eden)

<img src = "https://raw.githubusercontent.com/abraham-ai/eden/master/images/cover.png">

> You were in Eden, the garden of God. Every kind of precious stone adorned you: ruby, topaz, and diamond, beryl, onyx, and jasper, sapphire, turquoise, and emerald. Your mountings and settings were crafted in gold, prepared on the day of your creation.
>
> Ezekiel 28:13

Eden is a sandbox for [the Abraham project](http://abraham.ai) to deploy pretty much any python function as a hosted endpoint.

## Setting up a block

Hosting with `eden` requires minimal changes to your existing code. Each unit within `eden` is called a `Block`, they're the units which take certain inputs and generate art accordingly.

The first step is to configure `run()`.

```python
from eden.block import Block
from eden.datatypes import Image

eden_block = Block()
```

`run()` is supposed to be the function that runs every time someone wants to use this pipeline to generate art. For now it supports text, images, and numbers as inputs.

```python
my_args = {
        'prompt': 'let there be light', ## text
        'number': 12345,                ## numbers
        'input_image': Image()          ## images require eden.datatypes.Image()
    }

@eden_block.run(args = my_args)
def do_something(config):

    pil_image = config['input_image']
    some_number = config['number']

    return {
        'text': 'hello world',  ## returning text
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
    logfile= 'logs.log',
    log_level= 'info',
    max_num_workers = 5
)
```

- `block` (`eden.block.Block`): The eden block you'd want to host.
- `port` (`int, optional`): Localhost port where the block would be hosted. Defaults to `8080`.
- `host` (`str`): specifies where the endpoint would be hosted. Defaults to `'0.0.0.0'`.
- `max_num_workers` (`int, optional`): Maximum number of tasks to run in parallel. Defaults to `4`.
- `redis_port` (`int, optional`): Port number for celery's redis server. Defaults to `6379`.
- `redis_host` (`str, optional`): Place to host redis for `eden.queue.QueueData`. Defaults to `"localhost"`.
- `requires_gpu` (`bool, optional`): Set this to `False` if your tasks dont necessarily need GPUs.
- `log_level` (`str, optional`): Can be 'debug', 'info', or 'warning'. Defaults to `'warning'`
- `exclude_gpu_ids` (`list, optional`): List of gpu ids to not use for hosting. Example: `[2,3]`. Defaults to `[]`
- `logfile`(`str, optional`): Name of the file where the logs would be stored. If set to `None`, it will show all logs on stdout. Defaults to `'logs.log'`
- `queue_name`(`str, optional`): Name of the celery queue used for the block. Useful when hosting multiple blocks with the same redis. (defaults on `celery`)

## Client

A `Client` is the unit that sends requests to a hosted block.

```python
from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')
```

After you start a task with `run()` as shown below, it returns a token as `run_response['token']`. This token should be used later on to check the task status or to obtain your results.

> **Note**: `Image()` is compatible with following types: `PIL.Image`, `numpy.array` and filenames (`str`) ending with `.jpg` or `.png`

```python
config = {
    'queue_name': 'celery', # specify block's queue if running multiple blocks
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('your_image.png')  ## Image() supports jpg, png filenames, np.array or PIL.Image
}

run_response = c.run(config)
```

Fetching results/checking task status using the token can be done using `fetch()`.

```python
results = c.fetch(token = run_response['token'])
print(results)
```

## Prometheus metrics out of the box

Eden supports the following internal metrics (`/metrics`) which have been exposed via prometheus:

* `num_queued_jobs`: Specifies the number of queued jobs
* `num_running_jobs`: Specifies the number of running jobs
* `num_failed_jobs`: Specifies the number of failed jobs
* `num_succeeded_jobs`: Specifies the number of succeeded jobs
