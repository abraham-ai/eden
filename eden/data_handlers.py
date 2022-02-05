from eden.image_utils import decode

from eden.datatypes import Image


class Decoder(object):
    def __init__(self):

        ## when you add more datatypes,
        ## update this map and add the new method below
        self.type_name_to_method_mapping = {
            "eden.datatypes.Image": self.decode_image_data
        }

    def decode_image_data(self, data: str):
        """
        converts str to pil image
        """
        return decode(data)

    def decode(self, data):
        """
        Looks for dicts which have a 'type' key and decodes them

        Args:
            response (dict): decoded data
        """

        if not isinstance(data, dict):
            data = dict(data)

        for key, value in data.items():

            if isinstance(value, dict):
                if "type" in list(value.keys()):

                    decoder_method = self.type_name_to_method_mapping[value["type"]]
                    data[key] = decoder_method(data[key]["data"])

        return data


class Encoder(object):
    def __init__(self):

        ## when you add more datatypes,
        ## update this list
        self.datatypes_to_encode = [
            Image,
        ]

    def encode(self, data: dict):
        """
        Looks for datatypes belonging to eden.dataypes and
        encodes them to send over the network

        Args:
            data (dict): dict containing stuff

        Returns:
            dict: encoded data ready to be converted into a json
        """
        for key, value in data.items():
            if type(value) in self.datatypes_to_encode:
                data[key] = value.encode()

        return data
