import time
from eden.client import Client
from eden.datatypes import Image, Video

## set up a client
c = Client(url="http://0.0.0.0:5656", username="abraham")

## define input args to be sent
config = {
    "input_image": Image(
        "../../images/cloud.jpg"
    ),  ## image require eden.datatypes.Image()
    "input_video": Video(
        "../../images/fingers.mp4"
    ),  ## video require eden.datatypes.Video()
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
