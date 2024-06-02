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


def receive_data(data):
    return pickle.loads(data)


def send_data(data):
    return pickle.dumps(data)


