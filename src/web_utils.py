import json

def json_link_reader(file_name):
    with open(file_name, "r") as file:
        return json.load(file) 
