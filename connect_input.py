import asyncio
from bleak import BleakClient
import binascii
from aioconsole import ainput
import numpy as np
import math
from scipy import signal

import json
import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

address = "0CE4468C-F05D-CE69-B2D9-F03D72FB9130"
writeUUID = "0000ffe9-0000-1000-8000-00805f9a34fb"
counter = 0
G = 9.8
debug = False
s = None

b, a = None, None
d, c = None, None
f, e = None, None

norm = 0
timeRecord, timeDiff = 0, 0

fs = num = 100
fdis = 10

x_value, y_value, z_value = np.array([0]*num), np.array([0]*num), np.array([0]*num)
hp_x, hp_y, hp_z = np.array([0]*num), np.array([0]*num), np.array([0]*num)

v_x, v_y, v_z = np.array([0]*num), np.array([0]*num), np.array([0]*num)
v_hp_x, v_hp_y, v_hp_z = np.array([0]*num), np.array([0]*num), np.array([0]*num)
vv_x, vv_y, vv_z = 0, 0, 0

p_x, p_y, p_z = np.array([0]*num), np.array([0]*num), np.array([0]*num)
p_hp_x, p_hp_y, p_hp_z = np.array([0]*num), np.array([0]*num), np.array([0]*num)
pp_x, pp_y, pp_z = 0, 0, 0

def filterHG():
    global fs  # Sampling frequency
    # Generate the time vector properly
    # t = np.arange(1000) / fs
    fc = 0.01  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    b, a = signal.butter(1, w, 'highpass')
    return [b, a]

def filterHG2():
    global fs  # Sampling frequency
    # Generate the time vector properly
    # t = np.arange(1000) / fs
    fc = 2  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    f, e = signal.butter(1, w, 'lowpass')
    return [f, e]

def filterLW():
    global fs  # Sampling frequency
    # Generate the time vector properly
    # t = np.arange(1000) / fs
    fc = 10  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    d, c = signal.butter(1, w, 'lowpass')
    return [d, c]

def getPos(x, y, z):
    global timeRecord, timeDiff
    if timeRecord==0:
        timeRecord = time.time_ns()
        timeDiff = 0
    else:
        temp = time.time_ns()
        timeDiff = (temp - timeRecord)/5000000.0
        timeRecord = temp

    global b, a
    global d, c
    global f, e

    # x_value.append(x)
    # y_value.append(y)
    # z_value.append(z)

    global x_value, y_value, z_value
    global hp_x, hp_y, hp_z

    x_value = np.append(x_value, x)
    y_value = np.append(y_value, y)
    z_value = np.append(z_value, z)

    temp_x = signal.filtfilt(b, a, x_value)
    temp_y = signal.filtfilt(b, a, y_value)
    temp_z = signal.filtfilt(b, a, z_value)

    hp_x = signal.filtfilt(d, c, temp_x)
    hp_y = signal.filtfilt(d, c, temp_y)
    hp_z = signal.filtfilt(d, c, temp_z)


    global norm
    norm = math.sqrt(hp_x[-1]*hp_x[-1] + hp_y[-1]*hp_y[-1] + hp_z[-1]*hp_z[-1])
    # if norm < 1:
    #     return

    global v_x, v_y, v_z
    global v_hp_x, v_hp_y, v_hp_z
    global vv_x, vv_y, vv_z

    temp = 0.05
    tempH = 10
    # vv_x = v_x[-1] + hp_x[-1]if tempH > norm > temp else v_x[-1]*0.9
    # vv_y = v_y[-1] + hp_y[-1] if tempH > norm > temp else v_y[-1]*0.9
    # vv_z = v_z[-1] + hp_z[-1] if tempH > norm > temp else v_z[-1]*0.9
    vv_x = v_x[-1] + hp_x[-1]/math.log2(norm*(2/temp)) if tempH > norm > temp else v_x[-1]*0.9
    vv_y = v_y[-1] + hp_y[-1]/math.log2(norm*(2/temp)) if tempH > norm > temp else v_y[-1]*0.9
    vv_z = v_z[-1] + hp_z[-1]/math.log2(norm*(2/temp)) if tempH > norm > temp else v_z[-1]*0.9

    if vv_x*v_x[-30] < -0.2:
        vv_x *= 0.5
    if vv_y*v_y[-30] < -0.2:
        vv_y *= 0.5
    if vv_z*v_z[-30] < -0.2:
        vv_z *= 0.5

    # vv_x = v_x[-1] + x *timeDiff
    # vv_y = v_y[-1] + y *timeDiff
    # vv_z = v_z[-1] + z *timeDiff

    v_x = np.append(v_x, vv_x)
    v_y = np.append(v_y, vv_y)
    v_z = np.append(v_z, vv_z)

    v_hp_x = signal.filtfilt(f, e, v_x)
    v_hp_y = signal.filtfilt(f, e, v_y)
    v_hp_z = signal.filtfilt(f, e, v_z) 

    # v_temp_x = signal.filtfilt(b, a, v_x)
    # v_temp_y = signal.filtfilt(b, a, v_y)
    # v_temp_z = signal.filtfilt(b, a, v_z) 
    # v_hp_x = signal.filtfilt(d, c, v_temp_x)
    # v_hp_y = signal.filtfilt(d, c, v_temp_y)
    # v_hp_z = signal.filtfilt(d, c, v_temp_z)  
     
    # global norm
    norm = math.sqrt(v_x[-1]*v_x[-1] + v_y[-1]*v_y[-1] + v_z[-1]*v_z[-1])  

    global p_x, p_y, p_z
    global p_hp_x, p_hp_y, p_hp_z
    global pp_x, pp_y, pp_z

    # # Version 0
    # pp_x = p_x[-1] + v_x[-1]
    # pp_y = p_y[-1] + v_y[-1]
    # pp_z = p_z[-1] + v_z[-1]

    # pp_x = p_x[-1] + v_x[-1] if norm > 0.1 else p_x[-1]
    # pp_y = p_y[-1] + v_y[-1] if norm > 0.1 else p_y[-1]
    # pp_z = p_z[-1] + v_z[-1] if norm > 0.1 else p_z[-1]

    # Version 1
    pp_x = p_x[-1] + v_hp_x[-1]
    pp_y = p_y[-1] + v_hp_y[-1]
    pp_z = p_z[-1] + v_hp_z[-1]
    
    # Version 2
    # pp_x = p_x[-1] + v_hp_x[-1] if abs(v_hp_x[-1])>0.2 else p_x[-1]
    # pp_y = p_y[-1] + v_hp_y[-1] if abs(v_hp_y[-1])>0.2 else p_y[-1]
    # pp_z = p_z[-1] + v_hp_z[-1] if abs(v_hp_z[-1])>0.6 else p_z[-1]

    # Version 3
    # pp_x = p_x[-1] + v_hp_x[-1] *timeDiff
    # pp_y = p_y[-1] + v_hp_y[-1] *timeDiff
    # pp_z = p_z[-1] + v_hp_z[-1] *timeDiff

    p_x = np.append(p_x, pp_x)
    p_y = np.append(p_y, pp_y)
    p_z = np.append(p_z, pp_z)

    p_hp_x = signal.filtfilt(d, c, p_x)
    p_hp_y = signal.filtfilt(d, c, p_y)
    p_hp_z = signal.filtfilt(d, c, p_z)

    # print("{:.2f}".format(p_hp_x[-1]))

    # if len(x_value)>20:
    # x_value.pop(0)
    # y_value.pop(0)
    # z_value.pop(0)
    np.delete(x_value, 0)
    np.delete(y_value, 0)
    np.delete(z_value, 0)

    np.delete(v_x, 0)
    np.delete(v_y, 0)
    np.delete(v_z, 0)
    # np.delete(v_hp_x, 0)
    # np.delete(v_hp_y, 0)
    # np.delete(v_hp_z, 0)
    # v_x = v_x[1:]
    # v_y = v_y[1:]
    # v_z = v_z[1:]
    # v_hp_x = v_hp_x[1:]
    # v_hp_y = v_hp_y[1:]
    # v_hp_z = v_hp_z[1:]

    np.delete(p_x, 0)
    np.delete(p_y, 0)
    np.delete(p_z, 0)

    # np.delete(p_hp_x, 0)
    # np.delete(p_hp_y, 0)
    # np.delete(p_hp_z, 0)

def rotate(x, y, z, v):
    # v: [v_x, v_y, v_z]
    m_x = np.array([
        [1, 0, 0],
        [0, math.cos(x), -math.sin(x)],
        [0, math.sin(x), math.cos(x)],
    ])
    m_y = np.array([
        [math.cos(y), 0, math.sin(y)],
        [0, 1, 0],
        [-math.sin(y), 0, math.cos(y)],
    ])
    m_z = np.array([
        [math.cos(z), -math.sin(z), 0],
        [math.sin(z), math.cos(z), 0],
        [0, 0, 1],
    ])
    res = np.dot(m_x, v)
    res2 = np.dot(m_y, res)
    res3 = np.dot(m_z, res2)
    return res3

def notification_handler(sender, dataList):
    global counter
    global debug
    """Simple notification handler which prints the data received."""
    length = len(dataList)//20

    for i in range(length):
        data = dataList[i*20:(i+1)*20]
        if debug:
            print("{0}: {1}".format(counter, binascii.hexlify(data)))
        if data[0:2]==b'\x55\x61':
            acc_x, acc_y, acc_z = int.from_bytes(data[2:4], "little", signed="True")/32768*16*G, int.from_bytes(data[4:6], "little", signed="True")/32768*16*G, int.from_bytes(data[6:8], "little", signed="True")/32768*16*G
            w_x, w_y, w_z = int.from_bytes(data[8:10], "little", signed="True")/32768*2000, int.from_bytes(data[10:12], "little", signed="True")/32768*2000, int.from_bytes(data[12:14], "little", signed="True")/32768*2000
            roll, pitch, yaw = int.from_bytes(data[14:16], "little", signed="True")/32768*180, int.from_bytes(data[16:18], "little", signed="True")/32768*180, int.from_bytes(data[18:20], "little", signed="True")/32768*180
            # g = [0, 0, 9.8] # if (abs(roll)<90 or not abs(pitch)<90) or (not abs(roll)<90 or abs(pitch)<90)  else [0, 0, -9.8]  # ^: XOR
            # [off_x, off_y, off_z] = rotate(-pitch/180*np.pi, -roll/180*np.pi, -yaw/180*np.pi, g)
            ref = [-acc_x, -acc_y, -acc_z]
            [off_x, off_y, off_z] = rotate(roll/180*np.pi, pitch/180*np.pi, yaw/180*np.pi, ref)
            getPos(off_x, off_y, off_z+9.81)

            if debug:
                print(f"{counter}: [roll: {roll}, pitch: {pitch}, yaw: {yaw}]")
                print(f"{counter}: [acc: {acc_x}, {acc_y}, {acc_z}, w: {w_x}, {w_y}, {w_z}]")
                print(f"{counter}: [off: {off_x}, {off_y}, {off_z}]")

            global p_x, p_y, p_z
            global p_hp_x, p_hp_y, p_hp_z, norm, timeDiff
            global v_hp_x, v_hp_y, v_hp_z
            global fs, fdis
            if counter%(fs//fdis) == 0:
                # PRINT OUTPUT
                # print("x: {:.2f}, y: {:.2f}, z: {:.2f}, n: {:.2f}, t: {:.5f}".format(p_hp_x[-1], p_hp_y[-1], p_hp_z[-1], norm, timeDiff))
                print("Pos x: {:.2f}, y: {:.2f}, z: {:.2f}, n: {:.2f}, t: {:.5f}".format(p_x[-1], p_y[-1], p_z[-1], norm, timeDiff))
                # print("Vec x: {:.2f}, y: {:.2f}, z: {:.2f}".format(v_x[-1], v_y[-1], v_z[-1]))
                # print("Filtered Vec x: {:.2f}, y: {:.2f}, z: {:.2f}".format(v_hp_x[-1], v_hp_y[-1], v_hp_z[-1]))
                # print("Filtered Acc x: {:.2f}, y: {:.2f}, z: {:.2f}".format(hp_x[-1], hp_y[-1], hp_z[-1]))
                if s!= None: 
                    m = {'x': p_hp_x[-1], 'y': p_hp_y[-1], 'z': p_hp_z[-1]}
                    data = json.dumps(m) 
                    s.sendall(bytes(data,encoding="utf-8"))

        if data[0:2]==b'\x55\x71':
            if data[2]==0x3a:
                h_x, h_y, h_z = int.from_bytes(data[4:6], "little", signed="True"), int.from_bytes(data[6:8], "little", signed="True"), int.from_bytes(data[8:10], "little", signed="True")
                print(f"{counter}: [mag: {h_x}, {h_y}, {h_z}]")
            elif data[2]==0x51:
                q = []
                for i in range(4, 12, 2):
                    q.append(int.from_bytes(data[i:i+2], "little", signed="True")/32768)
                print(f"{counter}: [quar: {q[0]}, {q[1]}, {q[2]}, {q[3]}]")
            elif data[2]==0x40:
                print("Humidity!!")
            elif data[2]==0x64:
                print("Power!!")
            
        counter += 1

async def main(address):
    async with BleakClient(address) as client:
        global b, a
        b, a = filterHG()

        global d, c
        d, c = filterLW()

        global f, e
        f, e = filterHG2()

        await client.start_notify(13, notification_handler)

        instruct = {
            "M": b'\xff\xaa\x27\x3a\x00', 
            "Q": b'\xff\xaa\x27\x51\x00', 
            "H": b'\xff\xaa\x27\x40\x00',
            "P": b'\xff\xaa\x27\x64\x00',
            "R": b'\xff\xaa\x00\x01\x00',
        }
        rate = {
            "1":    b'\xff\xaa\x03\x03\x00',    # 1Hz
            "2":    b'\xff\xaa\x03\x04\x00',    # 2Hz
            "3":    b'\xff\xaa\x03\x05\x00',    # 5Hz
            "4":    b'\xff\xaa\x03\x06\x00',    # 10Hz
            "5":    b'\xff\xaa\x03\x09\x00',    # 100Hz
            "6":    b'\xff\xaa\x03\x0a\x00',    # 200Hz
        }


        # global s
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((HOST, PORT))
            
        while True:
            msgWrite = await ainput("")
            if msgWrite in instruct:
                await client.write_gatt_char(writeUUID, instruct[msgWrite])
            elif msgWrite in rate:
                await client.write_gatt_char(writeUUID, rate[msgWrite])
                await client.write_gatt_char(writeUUID, b'\xff\xaa\x00\x00\x00')
            elif msgWrite == "E": 
                print("Exit!!")
                break

        await client.stop_notify(13)

asyncio.run(main(address))
