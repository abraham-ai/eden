from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

setup_response = c.setup()

config = {
    'prompt': 'let there be light',
    'number': 2233,
    'input_image': Image('test_images/krusty_krab.png')  ## Image() supports jpg, png filenames, np.array or PIL.Image
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
time.sleep(5)


'''
task should be complete by now, this time fetch() returns the output as: {'status': 'complete', 'output': {your_outputs}}
'''
results = c.fetch(token = run_response['token'])
pil_image = results['output']['image']
pil_image.save('saved_from_server.png')