import time
from eden.client import Client
from eden.datatypes import Image

## set up a client
c = Client(url="http://0.0.0.0:5656", username="abraham")

# get server's identity
generator_id = c.get_generator_identity()
print(generator_id)

## define input args to be sent
config = {
    "width": 224,  ## width
    "height": 224,  ## height
    "input_image": Image(
        "../../images/cloud.jpg"
    ),  ## images require eden.datatypes.Image()
}

# start the task
run_response = c.run(config)

# check status of the task, returns the output too if the task is complete
results = c.fetch(token=run_response["token"])
print(results)

# one eternity later
time.sleep(5)

## check status again, hopefully the task is complete by now
results = c.fetch(token=run_response["token"])
print(results)
