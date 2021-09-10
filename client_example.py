from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

config = {
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('cloud.jpg')  ## Image() supports jpg, png filenames, np.array or PIL.Image
}

'''
starts the task
'''
run_response = c.run(config)
print(run_response)

'''
returns the output if the task is complete, else returns {'status': 'running'}
'''
results = c.fetch(token = run_response['token'])
print(results)

'''
one eternity later
'''
import time
time.sleep(2)


'''
change the config mid-task
'''

config['prompt'] = 'abraham really likes carrots'
resp = c.update_config(token = run_response['token'], config = config)
print(resp)

'''
another eternity later
'''
import time
time.sleep(10)


'''
if the task is complete: 
    returns {'status': 'complete', 'output': {your_outputs}}
else
    returns {'status': 'running'}
'''
results = c.fetch(token = run_response['token'])
print(results)
pil_image = results['output']['image']
pil_image.save('saved_from_server.png')
