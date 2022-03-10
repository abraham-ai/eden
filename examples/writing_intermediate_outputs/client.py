import time
from eden.client import Client
from eden.datatypes import Image

## set up a client
c = Client(url="http://0.0.0.0:5656", username="abraham")

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

for i in range(10):
    # wait for a while
    time.sleep(0.5)

    ## check status again
    results = c.fetch(token=run_response["token"])
    print(results["output"])

    ## save either intermediate creations or the final one
    try:
        results["output"]["intermediate_creation"].save(f"{i}.png")
    except KeyError:
        results["output"]["creation"].save(f"final.png")

    print("\n")
