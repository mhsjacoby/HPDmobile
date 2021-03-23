#this runs in antsle VM
import socket

def main():
    while True:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('192.168.0.206', 8000))
        serversocket.listen(5) # become a server socket, maximum 5 connections
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print(buf)
        #serversocket.sendall(b'Hello, world')
if __name__ == '__main__':
    main()
        
