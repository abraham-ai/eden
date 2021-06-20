from .datatypes import Image
from .image_utils import decode

def parse_for_sending_request(config: dict = {}):
    for key, value in config.items():
        
        if isinstance(value, Image):
            config[key] = value.__call__()

    return config

def parse_for_taking_request(response: dict = {}):

    for key, value in response.items():

        if isinstance(value, dict):
            if 'type' in list(value.keys()):
                
                if value['type'] == 'eden.datatypes.Image':
                    response[key] = decode(response[key]['data'])

                '''
                as we add more datatypes, just add them in here like: 

                if value['type'] == 'eden.datatypes.some_type':
                    response[key] = decode_some_type(response[key]['data'])

                '''
    return response


def parse_response_after_run(response: dict = {}):

    resp_out = response['output']

    for key, value in resp_out.items():

        if isinstance(value, dict):
            if 'type' in list(value.keys()):
                
                if value['type'] == 'eden.datatypes.Image':
                    resp_out[key] = decode(resp_out[key]['data'])

                '''
                as we add more datatypes, just add them in here like: 

                if value['type'] == 'eden.datatypes.some_type':
                    resp_out[key] = decode_some_type(resp_out[key]['data'])

                '''

    response['output'] = resp_out
    return response


