import socket, sys
import threading

from typing import (
    List,
)

HOST = '127.0.0.1'
PORT = 7002
BUFFER_SIZE = 1024

clientCount = 0

class SocketServer():

    def __init__(self, host=HOST, port=PORT):
        self.CLIENTS = [] 

        self.is_reading = True    
        self.threads : List[threading.Thread] = [] 

        self.s = None
        self.host = host
        self.port = port

    def startServer(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.host, self.port))
            self.s.listen(10)
            while self.is_reading:
                client_socket, addr = self.s.accept()
                print ('Connected with ' + addr[0] + ':' + str(addr[1]))
                global clientCount
                clientCount = clientCount+1
                print (clientCount)
                # register client
                self.CLIENTS.append(client_socket)
                new_thread = threading.Thread(target=self.playerHandler, args=(client_socket,))
                new_thread.start()
                self.threads.append(new_thread)
            # s.close()
        except socket.error as msg:
            print ('Could Not Start Server Thread. Error Code : ') #+ str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def stopServer(self):
        print("Server stop!")
        for thread in self.threads:
            thread.join()
        self.is_reading = False
        self.s.close()

   #client handler :one of these loops is running for each thread/player   
    def playerHandler(self, client_socket):
        #send welcome msg to new client
        # client_socket.send(bytes('{"type": "bet","value": "1"}', 'UTF-8'))
        while self.is_reading:
            data = client_socket.recv(BUFFER_SIZE)
            if not data: 
                break
            #print ('Data : ' + repr(data) + "\n")
            #data = data.decode("UTF-8")
            # broadcast
            for client in self.CLIENTS.values():
                client.send(data)

         # the connection is closed: unregister
        self.CLIENTS.remove(client_socket)
        #client_socket.close() #do we close the socket when the program ends? or for ea client thead?

    def broadcast(self, message):
        for c in self.CLIENTS:
            try:
                c.send(message.encode("utf-8"))
            except socket.error:                
                c.close()  # closing the socket connection
                self.CLIENTS.remove(c)  # removing the socket from the active connections list


    def _broadcast(self):        
        for sock in self.CLIENTS:           
            try :
                self._send(sock)
            except socket.error:                
                sock.close()  # closing the socket connection
                self.CLIENTS.remove(sock)  # removing the socket from the active connections list

    def _send(self, sock):        
        # Packs the message with 4 leading bytes representing the message length
        #msg = struct.pack('>I', len(msg)) + msg
        # Sends the packed message
        sock.send(bytes('{"type": "bet","value": "1"}', 'UTF-8'))