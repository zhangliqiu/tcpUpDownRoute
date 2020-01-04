import socket
from log import *
from time import sleep
from queue import Queue
from Extest import doppel

beEncry = False

BUFFSIZE = 1024*10

clientSqu = 0

def encrypt(buff):
    c = doppel(buff.hex())
    d = bytes.fromhex(c)
    return d
def decrypt(buff):
    c = doppel(buff.hex())
    d = bytes.fromhex(c)
    return d

class Client():
    def __init__(self):
        global clientSqu
        self.clientSocket = socket.socket()
        self.upSocket = socket.socket()
        self.downSocket = socket.socket()
        self.serverSocket = socket.socket()
        self.num = clientSqu
        self.clientSocketRecvBuff = b''
        self.downSocketRecvBuff = b''
        self.serverSocketRecvBuff = b''

        self.clientSocketSendBuff = b''
        self.upSocketSendBuff = b''
        self.serverSocketSendBuff = b''

        self.transDataSize = 0
        self.lastPrintSpeedTime = 0
        self.mode = ''
        clientSqu += 1

    def clientSelf(self):
        return self

    def closeAllSockets(self):        
        self.clientSocket.close()
        self.upSocket.close()
        self.downSocket.close()
        self.serverSocket.close()

    def recv(self, sock):
        try:
            buff = sock.recv(BUFFSIZE)
        except Exception as identifier:
            buff = b''
        return buff

    def send(self, sock, buff=b''):
        try:
            re = sock.send(buff)
        except Exception as identifier:
            re = -1

        return re

    #
    #
    #
    # clientSocket 的方法

    def clientSocketRecv(self):  # recv date from client
        if self.clientSocketRecvBuff != b'':
            return 0
        buff = self.recv(self.clientSocket)
        bl = len(buff)
        if bl == 0:
            return -1
        self.clientSocketRecvBuff = buff
        return bl

    def clientSocketSend(self):  # send data to client
        buff = self.clientSocketSendBuff
        return self.send(self.clientSocket, buff)
    #
    #
    #
    # upSocket 的方法

    def upSocketRecv(self):
        buff = self.recv(self.upSocket)
        bl = len(buff)
        if bl == 0:
            return -1
        return bl

    def upSocketSend(self):
        buff = self.upSocketSendBuff
        if beEncry:
            if self.mode == 'client' or self.mode == 'server':
                buff = encrypt(buff)

        return self.send(self.upSocket, buff)
    #
    #
    #
    # downSocket 的方法

    def downSocketRecv(self):
        if self.downSocketRecvBuff != b'':
            return 0
        buff = self.recv(self.downSocket)
        bl = len(buff)

        if bl == 0:
            return -1
        if beEncry :
            if self.mode == 'client' or self.mode == 'server':
                buff = decrypt(buff)
        self.downSocketRecvBuff = buff
        return bl

    def serverSocketRecv(self):
        if self.serverSocketRecvBuff != b'':
            return 0
        buff = self.recv(self.serverSocket)
        bl = len(buff)
        if bl == 0:
            return -1
        self.serverSocketRecvBuff = buff
        return bl

    def serverSocketSend(self):
        buff = self.serverSocketSendBuff
        return self.send(self.serverSocket, buff)
