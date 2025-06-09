import json


class DataManager():
    def __init__(self):
        pass

    def get_data(file):
        with open(file, "r") as f:
            data = json.load(f)
        f.close()
        return data

    def write_data(file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
