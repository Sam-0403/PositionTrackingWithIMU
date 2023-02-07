import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

import socket
import json

import numpy as np
from scipy import signal

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# fig = plt.figure(figsize=[10, 10])
# ax  = fig.add_subplot(1, 1, 1, projection='3d')
ax = plt.axes(projection='3d')

limit = (-100, 100)

index = count()

x, y, z = 0, 0, 0

# x_value, y_value, z_value = [0], [0], [0]

# v_x, v_y, v_z = np.array([0]), np.array([0]), np.array([0])
# v_hp_x, v_hp_y, v_hp_z = np.array([0]), np.array([0]), np.array([0])
# vv_x, vv_y, vv_z = 0, 0, 0

# p_x, p_y, p_z = np.array([0]), np.array([0]), np.array([0])
# p_hp_x, p_hp_y, p_hp_z = np.array([0]), np.array([0]), np.array([0])
# pp_x, pp_y, pp_z = 0, 0, 0

# ans_x, ans_y, ans_z = 0, 0, 0

def filter():
    fs = 200  # Sampling frequency
    # Generate the time vector properly
    # t = np.arange(1000) / fs
    fc = 0.1  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    b, a = signal.butter(1, w, 'highpass')
    return [b, a]
    # output = signal.filtfilt(b, a, signalc)

def animate(i):
    # global x_value, y_value, z_value
    # global p_x, p_y, p_z
    # global p_hp_x, p_hp_y, p_hp_z
    # global ans_x, ans_y, ans_z
    global x, y, z
    plt.cla()
    ax.axes.set_xlim(limit)
    ax.axes.set_ylim(limit)
    ax.axes.set_zlim(limit)
    # if abs(p_x[-1]) > 4:
    #     ans_x += p_x[-1]/5
    # if abs(p_y[-1]) > 4:
    #     ans_y += p_y[-1]/5
    # if abs(p_z[-1]) > 4:
    #     ans_z += p_z[-1]/5
    # ax.plot3D([p_x[-1]], [p_y[-1]], [p_z[-1]], 'red', marker='o', markersize=5)
    # ax.plot3D([ans_x], [ans_y], [ans_z], 'red', marker='o', markersize=5)
    # ax.plot3D([p_hp_x[-1]], [p_hp_y[-1]], [p_hp_z[-1]], 'red', marker='o', markersize=5)
    ax.plot3D([x], [y], [z], 'red', marker='o', markersize=5)
    ax.annotate('x: {:.2f}, y: {:.2f}, z: {:.2f}'.format(x, y, z), xy=(0, 0))

def start_socket():
    [b, a] = filter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(256)
                    data = data.decode("utf-8")
                    data = json.loads(data)

                    global x, y, z
                    x, y, z = data["x"], data["y"], data["z"]

                    # x_value.append(x)
                    # y_value.append(y)
                    # z_value.append(z)

                    # global v_x, v_y, v_z
                    # global v_hp_x, v_hp_y, v_hp_z
                    # global vv_x, vv_y, vv_z

                    # vv_x = v_x[-1] + x
                    # vv_y = v_y[-1] + y
                    # vv_z = v_z[-1] + z

                    # v_x = np.append(v_x, vv_x)
                    # v_y = np.append(v_y, vv_y)
                    # v_z = np.append(v_z, vv_z)

                    # v_hp_x = signal.filtfilt(b, a, v_x)
                    # v_hp_y = signal.filtfilt(b, a, v_y)
                    # v_hp_z = signal.filtfilt(b, a, v_z)
                    # # print("Filtered")
                    # # except:
                    # #     continue

                    # global p_x, p_y, p_z
                    # global p_hp_x, p_hp_y, p_hp_z
                    # global pp_x, pp_y, pp_z

                    # pp_x = p_x[-1] + v_hp_x[-1]
                    # pp_y = p_y[-1] + v_hp_y[-1]
                    # pp_z = p_z[-1] + v_hp_z[-1]

                    # p_x = np.append(p_x, pp_x)
                    # p_y = np.append(p_y, pp_y)
                    # p_z = np.append(p_z, pp_z)

                    # p_hp_x = signal.filtfilt(b, a, p_x)
                    # p_hp_y = signal.filtfilt(b, a, p_y)
                    # p_hp_z = signal.filtfilt(b, a, p_z)

                    # if len(x_value)>50:
                    #     x_value.pop(0)
                    #     y_value.pop(0)
                    #     z_value.pop(0)

                    #     np.delete(v_x, 0)
                    #     np.delete(v_y, 0)
                    #     np.delete(v_z, 0)
                    #     np.delete(v_hp_x, 0)
                    #     np.delete(v_hp_y, 0)
                    #     np.delete(v_hp_z, 0)

                    #     np.delete(p_x, 0)
                    #     np.delete(p_y, 0)
                    #     np.delete(p_z, 0)
                    #     np.delete(p_hp_x, 0)
                    #     np.delete(p_hp_y, 0)
                    #     np.delete(p_hp_z, 0)

                    # # print(f"v: {v_x[-1]}")
                    # # print(f"p: {p_x[-1]}")

                except Exception as e: 
                    # print(e)
                    pass
                
                if not data:
                    break

# start_socket()

readThread = threading.Thread(target=start_socket)
readThread.setDaemon(True)
readThread.start()

ani = FuncAnimation(plt.gcf(), animate, interval=500)
ax.axes.set_xlim(limit)
ax.axes.set_ylim(limit)
ax.axes.set_zlim(limit)
# plt.tight_layout()
plt.show()