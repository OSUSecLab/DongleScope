import json


def get_config(dongle):
    if type(dongle) is int:
        return Config(dongle)
    else:
        return None


class Config(object):
    i = 0
    name = ""
    mode = 0  # 0 for wifi, 1 for Bluetooth, 2 for BLE
    address = ""
    port = 0
    uuid = ""  # {service: [read_characteristic, write_characteristic]}

    def __init__(self, i):
        self.i = i
        data = json.load(open("config.json"))
        item = data.get(str(i))
        self.name = str(item['name'])
        self.mode = item['mode']
        self.address = str(item['address'])
        self.port = item['port']
        self.uuid = item['uuid']



