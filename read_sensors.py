import socket
import threading

is_running = True

def get_input():
    global is_running

    while is_running:
        c = input()
        if c=="q":
            is_running = False

#connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1',7002))

read_thread = threading.Thread(target=get_input)
read_thread.start()

while is_running:
    #wait for server commands to do things, now we will just display things
    data = client_socket.recv(1024)     
    print(data.decode("utf-8"))

    if not data:
        break

read_thread.join()