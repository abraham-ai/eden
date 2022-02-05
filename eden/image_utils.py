import PIL
import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO


def _encode_numpy_array_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if image.shape[-1] == 3:
        _, buffer = cv2.imencode(".jpg", image)

    elif image.shape[-1] == 4:
        _, buffer = cv2.imencode(".png", image)

    image_as_text = base64.b64encode(buffer)

    return image_as_text


def _encode_pil_image(image):
    opencv_image = np.array(image)
    image_as_text = _encode_numpy_array_image(image=opencv_image)

    return image_as_text


def _encode_image_file(image):
    pil_image = Image.open(image)

    return _encode_pil_image(pil_image)


def encode(image):

    if (
        type(image) == np.ndarray
        or type(image) == str
        or isinstance(
            image,
            (
                PIL.JpegImagePlugin.JpegImageFile,
                PIL.PngImagePlugin.PngImageFile,
                PIL.Image,
            ),
        )
    ):

        if type(image) == np.ndarray:
            image_as_text = _encode_numpy_array_image(image)

        elif type(image) == str:
            image_as_text = _encode_image_file(image)

        else:
            image_as_text = _encode_pil_image(image)

        return image_as_text.decode("ascii")

    else:
        raise Exception(
            "expected numpy.array, PIL.Image or str, not: ", str(type(image))
        )


def decode(jpg_as_text):
    pil_image = Image.open(BytesIO(base64.b64decode(jpg_as_text)))
    return pil_image
