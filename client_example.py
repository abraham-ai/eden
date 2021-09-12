import time

from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

config = {
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('cloud.jpg')  ## Image() works on PIL.Image, numpy.array and on jpg an png files (str)
}

# starts the task
run_response = c.run(config)
print(run_response)

#after a while
time.sleep(1)

# returns the output if the task is complete, else returns {'status': 'running'}
results = c.fetch(token = run_response['token'])
print(results)

# one eternity later
time.sleep(1)

# change the config mid-task
config['prompt'] = 'abraham really likes carrots'
resp = c.update_config(token = run_response['token'], config = config)
print(resp)

# another eternity later
time.sleep(5)

'''
if the task is complete: 
    returns {'output': {your_outputs}}
'''
results = c.fetch(token = run_response['token'])
print(results)

## saving output images
pil_image = results['output']['image']
pil_image.save('saved_from_server.png')

# stop host after 0 seconds
c.stop_host(time = 0)
