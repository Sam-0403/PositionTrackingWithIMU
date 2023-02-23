from bleak import BleakScanner, BLEDevice, BleakClient
from modules.server import SocketServer

import time
import asyncio
import aioconsole
import threading
import numpy as np
from math import cos, sin
from config import config
import os

from modules.handler import Handler

from typing import (
    List,
)

is_running = True

def rotate(x, y, z, v):
    # v: [v_x, v_y, v_z]
    m_rot = np.array([
        [cos(z)*cos(y), cos(z)*sin(y)*sin(x)-sin(z)*cos(x), cos(z)*sin(y)*cos(x)+sin(z)*sin(x)],
        [sin(z)*cos(y), sin(z)*sin(y)*sin(x)+cos(z)*cos(x), sin(z)*sin(y)*cos(x)-cos(z)*sin(x)],
        [-sin(y), cos(y)*sin(x), cos(y)*cos(x)],
    ])
    return np.dot(m_rot, v)

class BLESender:
    def __init__(self):
        pass

    async def _scan(self, name:str = "", callback = None):
        """
        Scan the devices with specific name,
        send the scanned device list to callback function.
        """
        devices = None
        devices = await BleakScanner.discover()

        while devices==None:
            time.sleep(0.1)
        
        await aioconsole.aprint("Device scanned: ", end="")
        await aioconsole.aprint(devices)

        await callback([d for d in devices if (not d.name==None) and (name in d.name)])

    def scan(self, name:str = "", callback = None):
        asyncio.run(self._scan(name, callback))

    # def print_devices(devices:List[BLEDevice]):
    #     try:
    #         for d in devices:
    #             print(d)
    #     except Exception as e:
    #         print(e)

    async def service_explore(self, device):
        """
        Code from bleak/example/service_explorer.py
        """
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

    async def get_device_to_connect(self, devices):
        """
        Get a list as input as return corresponding devices
        """
        if devices == []:
            return []
        # while True:
        #     c = await aioconsole.ainput("Devices to connect (ex: 1, 3, 5): ")
        #     # print("c: ", c)
        #     if c:
        #         indices = list(map(int, c.split(",")))
        #         # print(devices)
        #         for i in indices:
        #             devices_to_connect.append(devices[i])
        #         break
        # global device_dict, devices_to_connect
        device_exist = [False]*6
        for d in devices:
            if d.name in config.device_dict:
                device_exist[config.device_dict[d.name]] = True
                config.devices_to_connect[config.device_dict[d.name]] = d
        
        for exist in device_exist:
            if not exist:
                await aioconsole.aprint("Some devices are missed.")
                # await scan("WT", devices_scanned)
                # os._exit(0)

    def is_connected(self):
        # global device_dict, devices_to_connect

        if None in config.devices_to_connect:
            return False
        else:
            return True
        
        # while True:
        #     if None in devices_to_connect:
        #         time.sleep(0.1)
        #     else:
        #         break

    async def devices_scanned(self, devices:List[BLEDevice]):
        """
        Run service_explore for each device,
        then get input list (ex: [0, 1]) as device_to_connect
        """
        try:
            await aioconsole.aprint(devices)
            for d, index in zip(devices, range(len(devices))):
                await aioconsole.aprint(f"[{index}] {d}")
                # await aioconsole.aprint("To explore server, press (e: explore, any: pass): ", end="")
                # while True:
                #     c = await aioconsole.ainput("")
                #     if c=="e":
                #         await service_explore(d)
                #         break
                #     else:
                #         break

            await self.get_device_to_connect(devices)
                
        except Exception as e:
            print(e)


    async def connect_to_device(self, name, address):
        """
        Async function for setting up the connection for one device,
        requesting for quaternion at the given sample rate
        """
        loop = asyncio.get_event_loop()
        
        await aioconsole.aprint("starting", address, "loop")
        async with BleakClient(address, loop=loop, timeout=30.0) as client:
            await aioconsole.aprint("Connect to", address)
            handler = Handler(config.device_dict[name], client, config.instruction, config.write_handler)
            config.clients.append(client)
            config.handlers.append(handler)
            await asyncio.sleep(1.0, loop=loop)
            # try:
            await client.start_notify(config.notify_handler, handler.notification_handler)
            try:
                await client.write_gatt_char(config.write_handler, config.instruction["Q"])
            except:
                print("Write Error")
            global is_running
            while is_running:
                await asyncio.sleep(1/config.f_sample, loop=loop)
                # try:
                #     await client.write_gatt_char(write_handler, instruction["Q"])
                # except:
                #     print("Write Error")
            await client.stop_notify(config.notify_handler)
            # except Exception as e:
            #     await aioconsole.aprint(e)

    async def send_broadcast_data(self, s:SocketServer):
        """
        Async function for reading the buffers and broadcast with the TCP socket server
        """
        await aioconsole.aprint("starting socket loop")
        loop = asyncio.get_event_loop()

        global is_running
        while is_running:
            data = ""
            for handler in config.handlers:
                buffer = handler.get_current_buffer()
                data += str(buffer["Index"]) + \
                        " " + \
                        " ".join(map(str, buffer["Acc"])) + \
                        " " + \
                        " ".join(map(str, buffer["Gyro"])) + \
                        " " + \
                        " ".join(map(str, buffer["Quat"])) + \
                        " "
                # await aioconsole.aprint(f"[{sender_buffer[sender]}] send")
            # s.broadcast(data[:-1])
            s.broadcast(data)
            await asyncio.sleep(1/config.f_sample, loop=loop)

    async def _connect_thread(self):
        await asyncio.gather(
            *(self.connect_to_device(d.name, d.address) for d in config.devices_to_connect)
        )

    async def _socket_thread(self, s):
        await asyncio.gather(
            *(self.send_broadcast_data(s) for _ in range(1))
        )

    async def _connect_and_broadcast(self, s):
        """
        Run connect_to_device and send_broadcast_data coroutine with asyncio
        """
        if not config.devices_to_connect:
            return
        
        self.connect_thread = threading.Thread(target=lambda: asyncio.run(self._connect_thread()))
        self.connect_thread.setDaemon(True)
        self.connect_thread.start()

        self.socket_thread = threading.Thread(target=lambda: asyncio.run(self._socket_thread(s)))
        self.socket_thread.setDaemon(True)
        self.socket_thread.start()
    
    def connect_and_broadcast(self, s):
        asyncio.run(self._connect_and_broadcast(s))

async def get_input():
    """
    Functions for reading commands when all setup finished
    """
    await aioconsole.aprint("Command (q: quit, ls: list, d: data) >> ")
    while True:
        c = await aioconsole.ainput("")
        if c == "q": 
            global is_running
            is_running = False
            await aioconsole.aprint("Exit!!")
            break
        if c == "ls": 
            for d in config.devices_to_connect:
                await aioconsole.aprint(d)
        # if c == "d":
        #     for acc, ang_vel, ang, quat, i in zip(acc_buffer, ang_vel_buffer, ang_buffer, quat_buffer, range(len(sender_buffer))):
        #         await aioconsole.aprint(f"Sender [{i}]: ")
        #         await aioconsole.aprint(f"\t Acc: ", end="")
        #         await aioconsole.aprint(acc)
        #         await aioconsole.aprint(f"\t Ang_Vel: ", end="")
        #         await aioconsole.aprint(ang_vel)
        #         await aioconsole.aprint(f"\t Ang: ", end="")
        #         await aioconsole.aprint(ang)
        #         await aioconsole.aprint(f"\t Quat: ", end="")
        #         await aioconsole.aprint(quat)

if __name__ == "__main__":
    """
    Instructions:
        --------
        1. Open all ble devices.
        2. Set up the device name in scan function
        3. Type: `e` to explore each scanned device services, `other` to pass           
        4. Input a list to select devices to connect
        5. Type: `q` to quit, `ls` to list devices_to_connect, `d` to show buffer data
        --------
    """
    ble_sender = BLESender()

    s = SocketServer(config.host, config.port)
    server_thread = threading.Thread(target=s.startServer)
    server_thread.start()

    while not ble_sender.is_connected():
        ble_sender.scan("WT", ble_sender.devices_scanned)

    ble_sender.connect_and_broadcast(s)
    
    asyncio.run(get_input())

    s.stopServer()
    
    ble_sender.connect_thread.join()
    ble_sender.socket_thread.join()

    server_thread.join()
