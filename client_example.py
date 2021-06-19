from eden.client import Client
from eden.image_utils import decode, encode

c = Client(url = 'http://127.0.0.1:5656', username= 'abraham')

setup_response = c.setup()

config = {
    'prompt': 'let there be light',
    'input_image': encode('test_images/krusty_krab.png')  ## encode() supports jpg, png files, np.array or PIL.Image
}

run_response = c.run(config)

# # Convert back to PIL and save
pil_image = decode(run_response['output']['image'])
pil_image.save('from_server.png')
