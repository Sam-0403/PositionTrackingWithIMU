from bleak import BleakScanner, BLEDevice, BleakClient

# from console.utils import wait_key

import time
import asyncio
import aioconsole
import socket

from typing import (
    List,
)

devices_to_connect : List[BLEDevice] = None
clients : List[BleakClient] = []

acc_buffer = []
ang_vel_buffer = []
ang_buffer = []
quat_buffer = []
sender_buffer = {}

notify_handler = 13
write_handler = 16

is_running = True

instruction = {
    "M": b'\xff\xaa\x27\x3a\x00', 
    "Q": b'\xff\xaa\x27\x51\x00', 
    "H": b'\xff\xaa\x27\x40\x00',
    "P": b'\xff\xaa\x27\x64\x00',
    "R": b'\xff\xaa\x00\x01\x00',
}

host, port = "127.0.0.1", 7002

f_sample = 50

async def scan(name:str = "", callback = None):
    devices = None
    devices = await BleakScanner.discover()

    while devices==None:
        time.sleep(0.1)
    
    print("Device scanned: ", end="")
    print(devices)

    await callback([d for d in devices if (not d.name==None) and (name in d.name)])

def print_devices(devices:List[BLEDevice]):
    try:
        for d in devices:
            # if "WT901BLE" in d.name:
            print(d)
            # print(d.name)
    except Exception as e:
        print(e)

async def service_explore(device):
    async with BleakClient(device.address) as client:
        await aioconsole.aprint(f"Connected: {client.is_connected}")

        for service in client.services:
            await aioconsole.aprint(f"[Service] {service}")
            for char, index in zip(service.characteristics, range(len(service.characteristics))):
                await aioconsole.aprint(f"[{index}] ", end="")
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                        await aioconsole.aprint(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                        )
                    except Exception as e:
                        await aioconsole.aprint(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}"
                        )

                else:
                    value = None
                    await aioconsole.aprint(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                    )

                for descriptor in char.descriptors:
                    try:
                        value = bytes(
                            await client.read_gatt_descriptor(descriptor.handle)
                        )
                        await aioconsole.aprint(
                            f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                    except Exception as e:
                        await aioconsole.aprint(
                            f"\t\t[Descriptor] {descriptor}) | Value: {e}")
        # add_list = await aioconsole.ainput("Characteristics you need (ex: 1, 3, 5): ")

async def get_device_to_connect(devices):
    devices_to_connect = []
    while True:
        c = await aioconsole.ainput("Devices to connect (ex: 1, 3, 5): ")
        # print("c: ", c)
        if c:
            indices = list(map(int, c.split(",")))
            # print(devices)
            for i in indices:
                devices_to_connect.append(devices[i])
            break
    return devices_to_connect

async def devices_scanned(devices:List[BLEDevice]):
    try:
        await aioconsole.aprint(devices)
        for d, index in zip(devices, range(len(devices))):
            await aioconsole.aprint(f"[{index}] {d}")
            await aioconsole.aprint("To explore server, press (e: explore, any: pass): ", end="")
            while True:
                c = await aioconsole.ainput("")
                if c=="e":
                    await service_explore(d)
                    break
                else:
                    break

        global devices_to_connect
        devices_to_connect = await get_device_to_connect(devices)
        # await get_input()
            
    except Exception as e:
        print(e)

def notification_notify_handler(sender, data):
    global sender_buffer, acc_buffer, ang_vel_buffer, ang_buffer
    acc = [0]*3
    for i, j in zip(range(2, 8, 2), range(3)):
        acc[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*16, 5)
    ang_vel = [0]*3
    for i, j in zip(range(8, 14, 2), range(3)):
        ang_vel[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*2000, 5)
    ang = [0]*3
    for i, j in zip(range(14, 20, 2), range(3)):
        ang[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*180, 5)
    
    acc_buffer[sender_buffer[sender]] = list(acc)
    ang_vel_buffer[sender_buffer[sender]] = list(ang_vel)
    ang_buffer[sender_buffer[sender]] = list(ang)

def notification_write_handler(sender, data):
    global sender_buffer, quat_buffer
    quat = [0]*4
    for i, j in zip(range(4, 12, 2), range(4)):
        quat[j] = round(int.from_bytes(data[i:i+2], "little", signed="True")/32768*16, 5)

    quat_buffer[sender_buffer[sender]] = list(quat)

async def notification_handler(sender, data):
    global sender_buffer, acc_buffer, ang_vel_buffer, ang_buffer, quat_buffer
    """Simple notification handler which prints the data received."""
    # print("{0}: {1}".format(sender, len(data)))
    # print("{0}: {1}".format(counter, binascii.hexlify(data)))

    if sender not in sender_buffer:
        sender_buffer[sender] = len(acc_buffer)
        acc_buffer.append([0]*3)
        ang_vel_buffer.append([0]*3)
        ang_buffer.append([0]*3)
        quat_buffer.append([0]*4)

    while len(data)>=20:
        # print(data)
        if data[0:2]==b'\x55\x61':
            notification_notify_handler(sender, data)
            # await client.write_gatt_char(write_handler, instruction["Q"])
            
        if data[0:2]==b'\x55\x71':
            if data[2]==0x51:
                notification_write_handler(sender, data)
    
        data = data[20:]

    await aioconsole.aprint(f"[{sender_buffer[sender]}] data in")

    # await aioconsole.aprint(sender)
    # await aioconsole.aprint(f"[acc: {acc_x}, {acc_y}, {acc_z}, w: {w_x}, {w_y}, {w_z}]")
    # await aioconsole.aprint(f"{counter}: [roll: {roll}, pitch: {pitch}, yaw: {yaw}]")

def callback(sender, data):
    print(sender, data)

async def connect_to_device(address, loop):
    global clients, is_running
    await aioconsole.aprint("starting", address, "loop")
    async with BleakClient(address, loop=loop, timeout=10.0) as client:
        await aioconsole.aprint("Connect to", address)
        clients.append(client)
        try:
            # await client.write_gatt_char(write_handler, instruction["Q"])
            await client.start_notify(notify_handler, notification_handler)
            while is_running:
                await asyncio.sleep(1/f_sample, loop=loop)
                await client.write_gatt_char(write_handler, instruction["Q"])
            await client.stop_notify(notify_handler)
        except Exception as e:
            await aioconsole.aprint(e)

async def send_broadcast_data(loop):
    global sender_buffer
    global acc_buffer, quat_buffer
    await aioconsole.aprint("starting socket loop")
    try:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        broadcast_socket.connect((host, port))
        while is_running:
            await asyncio.sleep(1/f_sample, loop=loop)
            data = ""
            for sender in sender_buffer:
                data += " ".join( str(sender_buffer[sender]) + " " + map(str, acc_buffer[sender_buffer[sender]])) + " " + " ".join(map(str, quat_buffer[sender_buffer[sender]]) )
            broadcast_socket.sendall(data.encode('utf8'))
    except Exception as e:
        await aioconsole.aprint(e)

def connect_devices(loop):
    global devices_to_connect
    asyncio.gather(
        *(connect_to_device(d.address, loop) for d in devices_to_connect)
    )
    asyncio.gather(
        *(send_broadcast_data(loop))
    )

async def get_input():
    global devices_to_connect, sender_buffer, is_running
    global acc_buffer, ang_vel_buffer, ang_buffer, quat_buffer
    await aioconsole.aprint("Command (q: quit, ls: list, acc: acc) >> ")
    while True:
        c = await aioconsole.ainput("")
        if c == "q": 
            is_running = False
            await aioconsole.aprint("Exit!!")
            break
        if c == "ls": 
            for d in devices_to_connect:
                await aioconsole.aprint(d)
        if c == "d":
            for acc, ang_vel, ang, quat, i in zip(acc_buffer, ang_vel_buffer, ang_buffer, quat_buffer, range(len(sender_buffer))):
                await aioconsole.aprint(f"Sender [{i}]: ")
                await aioconsole.aprint(f"\t Acc: ", end="")
                await aioconsole.aprint(acc)
                await aioconsole.aprint(f"\t Ang_Vel: ", end="")
                await aioconsole.aprint(ang_vel)
                await aioconsole.aprint(f"\t Ang: ", end="")
                await aioconsole.aprint(ang)
                await aioconsole.aprint(f"\t Quat: ", end="")
                await aioconsole.aprint(quat)

async def main():
    global devices_to_connect, clients

    loop = asyncio.get_event_loop()

    await scan("WT901BLE", devices_scanned)

    connect_devices(loop)

    await get_input()
            

asyncio.run(main())