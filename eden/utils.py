from .datatypes import Image
from .image_utils import decode

import json
import time
import secrets, string

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


    if 'output' in list(response.keys()):
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

def write_json(dictionary: dict, path:str):
    with open(path, "w") as write_file:
        json.dump(dictionary, write_file, indent=4)

def update_json(dictionary: dict, path:str):
    data = load_json_as_dict(path)
    for key, value in dictionary.items():
        data[key] = value
    write_json(data, path)

def make_filename_and_token(results_dir, username):
    id = make_id(username)
    filename = results_dir + "/" + id + '.json'
    # print("filename:  ", filename)
    return filename, id

def generate_random_string(len):
    x = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(len))
    return x

def make_id(username):
    id = username + "_"+ str(int(time.time())) + "_" + generate_random_string(len = 8)
    return id

def get_filename_from_token(results_dir, id):
    filename = results_dir + "/" + id + '.json'
    return filename

def load_json_as_dict(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    
    return data 
