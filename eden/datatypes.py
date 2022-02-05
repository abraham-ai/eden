from .image_utils import encode


class BaseDataType(object):
    def __init__(self, data=None):
        """
        A base abstraction over which all other eden's datatypes would be
        based on top of. n

        Args:
            data: Defaults to None.
        """
        self.type = "eden.datatypes.BaseDataType"
        self.data = data

    def encode(self):
        return {"data": self.data, "type": self.type}


class Image(BaseDataType):
    def __init__(self, image=None):
        """
        Wrapper to store/send images to and fro from an eden server.

        Args:
            image (numpy.array or PIL.Image or str, optional): Image to be stored. Defaults to None.
        """
        super().__init__()

        self.type = "eden.datatypes.Image"

        if image is not None:
            self.data = encode(image)
        else:
            pass
