from .image_utils import encode

class BaseDataType(object):
    def __init__(self):
        self.type = 'eden.datatypes.BaseDataType'
        self.data = ''
    

    def __call__(self):
        return {
            'data': self.data,
            'type': self.type
        }



class Image(BaseDataType):
    def __init__(self, image = None):
        super().__init__()
        self.type = 'eden.datatypes.Image'
        if image is not None:
            self.data =  encode(image)
        else:
            pass