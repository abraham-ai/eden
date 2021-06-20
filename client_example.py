from eden.client import Client
from eden.datatypes import Image

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

setup_response = c.setup()

config = {
    'prompt': 'let there be light',
    'input_image': Image('test_images/krusty_krab.png')  ## Image() supports jpg, png filenames, np.array or PIL.Image
}

run_response = c.run(config)

pil_image = run_response['output']['image']
pil_image.save('saved_from_server.png')