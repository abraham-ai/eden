from eden.block import Block
from eden.datatypes import Image
from eden.hosting import host_block

## eden <3 pytorch
from torchvision import models, transforms
import torch

model = models.resnet18(pretrained=True)
model = model.eval()  ## no dont move it to the gpu just yet :)

my_transforms = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

eden_block = Block()

my_args = {
    "width": 224,  ## width
    "height": 224,  ## height
    "input_image": Image(),  ## images require eden.datatypes.Image()
}


@eden_block.run(args=my_args, progress=False)
def do_something(config):
    global model

    pil_image = config["input_image"]
    pil_image = pil_image.resize((config["height"], config["width"]))

    device = config.gpu
    input_tensor = my_transforms(pil_image).to(device).unsqueeze(0)

    model = model.to(device)

    with torch.no_grad():
        pred = model(input_tensor)[0].cpu()
        index = torch.argmax(pred).item()
        value = pred[index].item()

    return {"value": value, "index": index}


host_block(
    block=eden_block,
    port=5656,
    logfile="logs.log",
    log_level="debug",
    max_num_workers=4,
    requires_gpu=True,
)
