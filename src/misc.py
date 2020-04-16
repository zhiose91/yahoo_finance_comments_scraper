from datetime import datetime
import json
import os


def json_reader(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

def sp_translate(text):
    return text.encode('ascii', 'ignore').decode('ascii')


def check_n_mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

class Logging:

    def __init__(self):
        pass

    @classmethod
    def current_datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_open(self, file_name):
        self.log_file = open(file_name, "a")

    def log(self, log_text, mode="main"):

        if mode == "main":
            pre_fix = ">>> "
        elif mode == "sub":
            pre_fix = "    "
        elif mode == "sub+":
            pre_fix = "        "
        else:
            pre_fix = ">>> "

        log_message = f'{self.current_datetime()} {pre_fix}{log_text}'
        print(log_message)
        self.log_file.write(f'{log_message}\n')

    def log_close(self):
        self.log_file.write("\n")
        self.log_file.close()
