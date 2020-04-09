import json
import sys

def json_reader(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

def sp_translate(text):
    return text.encode('ascii', 'ignore').decode('ascii')
