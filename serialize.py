# import json
#
#
# def receive_data(data) -> dict:
#     return json.loads(data.decode('utf-8'))
#
#
# def send_data(data):
#     return json.dumps(data).encode('utf-8')

import pickle
import json


def receive_data(data):
    return pickle.loads(data)


def send_data(data):
    return pickle.dumps(data)


def write_data_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)


def read_data_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data
