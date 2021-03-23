#this runs in CLIENT (the antsle VM)
import socket

def main():
    while (True):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        clientsocket.connect(('192.168.0.206', 8089))
        #str = "hello"
        #b = str.encode()
        #clientsocket.send(b)
        data = clientsocket.recv(1024)
        print("received data", data)
if __name__ == '__main__':
    main()

