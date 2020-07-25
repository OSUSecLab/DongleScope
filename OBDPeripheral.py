from pyble.handlers import PeripheralHandler, ProfileHandler


class MyDefault(ProfileHandler):
    UUID = "FFF0"
    _AUTOLOAD = False
    names = {
        "FFF1": "FFF1",
        "FFF2": "FFF2"
    }

    def initialize(self):
        print "[*] initialize called."
        pass

    def on_read(self, characteristic, data):
        print "[*] on_read called.  ",
        ans = []
        for b in data:
            if chr(ord(b)) != '\r':
                ans.append(chr(ord(b)))
        ret = "".join(ans)
        print str(characteristic) + " : " + ret
        return ret

    def on_write(self, characteristic, data):
        print "[*] on_write called."

    def on_notify(self, characteristic, data):
        # print "[*] on_notify called."
        return self.on_read(characteristic, data)


class MyPeripheral(PeripheralHandler):

    def initialize(self):
        self.addProfileHandler(MyDefault)

    def on_connect(self):
        print self.peripheral, "connect"

    def on_disconnect(self):
        print self.peripheral, "disconnect"

    def on_rssi(self, value):
        print self.peripheral, " update RSSI:", value

