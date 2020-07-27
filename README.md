# DongleScope

DongleScope is an automatic tool for detecting vulnerabilities on OBD-II dongles. With DongleScope, you can perform a few tests of an OBD-II (Wi-Fi, Bluetooth, or Bluetooth Low Energy (BLE) based) dongle on a real automobile, including:

1. Read test. Reading VIN from a vehicle using diagnostics [PIDs](https://en.wikipedia.org/wiki/OBD-II_PIDs).
2. Write test. DongleScope includes CAN bus messages that allow one to change the odometer unit on a Toyota RAV4.
3. Filter test. It will inject 10 arbitrary CAN bus message to test if the dongle has message filtering capability.
4. Fuzzing test (Note: this is very **dangerous** and will cause unpredicted consequences, we strongly recommend you do not try this on a vehicle in use).

For more details, please refer to our USENIX Security paper: [
Plug-N-Pwned: Comprehensive Vulnerability Analysis of OBD-II Dongles as A New Over-the-Air Attack Surface in Automotive IoT
](https://www.usenix.org/conference/usenixsecurity20/presentation/wen).

## Dependency

DongleScope is developed for **Python 2.7** and runs on the **MacOS** operating system. It depends on two python packages to achieve Bluetooth and BLE functions.

- [pyble](https://pypi.org/project/pyble/)
- [PyBluez](https://pypi.org/project/PyBluez/)

To install these dependencies, please run:

    pip install -r requirement.txt
    

## Running Example

The following shows an example of how DongleScope can query the VIN from a vehicle through an OBD-II dongle.

    >> python main.py
    ATZ
    ('Received', "OK")
    ATH1
    ('Received', "OK")
    AT SP 6
    ('Received', "OK")
    09 02
    ('Received', "7E8 10 14 49 02 01 4A 54 4D
                  7E8 21 52 46 52 45 56 32 45
                  7E8 ... ")

## How to run it

- Before the experiment, you must have a testing vehicle and an OBD-II dongle, and the dongle to be tested must be plugged into the OBD-II port of the vehicle (usually located under the dashboard, beneath the steering wheel column). [How to find it?](https://www.hum.com/port/)

- First, you need to specify the dongle configuration in **config.json** following the existing ones. For instance:

      "7": {
                "name": "Carly Adapter",
                "mode": 0,
                "address": "192.168.0.10",
                "port": 35000,
                "uuid": {}
            }
            
    Here it creates an index **7** for the dongle **Carly Adapter**, and you also need to specify the connection model (0 for Wi-Fi, 1 for Bluetooth Classic, and 2 for BLE), the ip address, and the port #.

- Next, you need to change the dongle index in [line 8](https://github.com/OSUSecLab/DongleScope/blob/master/main.py#L8) of main.py to your desired dongle index.

- Finally, run `python main.py`


## Citing

If you create a research work that uses our work, please cite our paper:

    @inproceedings {DongleScope:security20,
        title = {Plug-N-Pwned: Comprehensive Vulnerability Analysis of OBD-II Dongles as A New Over-the-Air Attack Surface in Automotive IoT},
        booktitle = {29th {USENIX} Security Symposium ({USENIX} Security 20)},
        year = {2020},
        address = {Boston, MA},
        url = {https://www.usenix.org/conference/usenixsecurity20/presentation/wen},
        publisher = {{USENIX} Association},
        month = aug,
    }
