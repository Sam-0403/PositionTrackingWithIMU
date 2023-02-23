from bleak import BleakScanner, BLEDevice, BleakClient
from modules.handler import Handler
from typing import (
    List,
)

class config:
    # devices_to_connect : List[BLEDevice] = [None]*6
    devices_to_connect : List[BLEDevice] = [None]

    clients : List[BleakClient] = []
    handlers : List[Handler] = []

    notify_handler = "0000ffe4-0000-1000-8000-00805f9a34fb"
    # notify_handler = 13
    write_handler = "0000ffe9-0000-1000-8000-00805f9a34fb"
    # write_handler = 16

    # is_running = True

    instruction = {
        "M": b'\xff\xaa\x27\x3a\x00', 
        "Q": b'\xff\xaa\x27\x51\x00', 
        "H": b'\xff\xaa\x27\x40\x00',
        "P": b'\xff\xaa\x27\x64\x00',
        "R": b'\xff\xaa\x00\x01\x00',
    }

    # device_dict = {
    #     "WT_LArm": 0,
    #     "WT_RArm": 1,
    #     "WT_LLeg": 2,
    #     "WT_RLeg": 3,
    #     "WT_Head": 4,
    #     "WT_Root": 5,
    # }
    device_dict = {
        "WT_Root": 0,
    }

    host, port = "127.0.0.1", 7002

    f_sample = 60