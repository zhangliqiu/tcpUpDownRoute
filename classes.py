import socket
from threading import Thread
from log import *
from time import sleep
from queue import Queue
from cryptography.fernet import Fernet


beEncry = True
key = b'OJ6koNlaMwsmg9jT3_JzH3mMvur00lbAXEv1Kfkt1D8='
Encry = Fernet(key)
BUFFSIZE = 19024

clientSqu = 0


def ck(value, name):
    print('name:    %s value:   %s' % (name, value))
    return value


class Client():
    def __init__(self):
        global clientSqu
        self.clientSocket = socket.socket()
        self.upSocket = socket.socket()
        self.downSocket = socket.socket()
        self.serverSocket = socket.socket()
        self.num = clientSqu
        self.clientSocketRecvQueue = Queue()
        #self.upSocketRecvQueue = Queue()
        self.downSocketRecvQueue = Queue()
        self.serverSocketRecvQueue = Queue()

        self.clientSocketSendQueue = Queue()
        self.upSocketSendQueue = Queue()
        #self.downSocketSendQueue = Queue()
        self.serverSocketSendQueue = Queue()

        self.transDataSize = 0
        self.lastPrintSpeedTime = 0
        self.clientFuckGFW = False
        self.serverFuckGFW = False
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
            peeraddr = sock.getpeername()
            buff = sock.recv(BUFFSIZE)
        except Exception as identifier:
            buff = b''
            peeraddr = ('', '')
        if buff == b'':
            log('num:   %s %s:%s disconnected' %
                (self.num, peeraddr[0], peeraddr[1]))
        return buff

    def send(self, sock, buff=b''):
        if buff == b'':
            return 0
        try:
            peeraddr = sock.getpeername()
            re = sock.send(buff)
        except Exception as identifier:
            re = 0
            peeraddr = ('', '')

        if re:
            log("num:   %s  send %s btyes to %s:%s" %
                (self.num, re, peeraddr[0], peeraddr[1]))
        return re

    #
    #
    #
    # clientSocket 的方法

    def clientSocketRecv(self):  # recv date from client
        buff = self.recv(self.clientSocket)

        bl = len(buff)
        if bl > 0:
            self.clientSocketRecvQueue.put(buff)
        return bl

    def clientSocketSend(self):  # send data to client
        if self.clientSocketSendQueue.qsize() > 0:
            return self.send(self.clientSocket, self.clientSocketSendQueue.get())
        return 0
    #
    #
    #
    # upSocket 的方法

    def upSocketRecv(self):
        buff = self.recv(self.upSocket)
        bl = len(buff)
        if bl > 0:
            log('upSocket recv %s bytes' % bl)
        return bl

    def upSocketSend(self):
        if self.upSocketSendQueue.qsize() > 0:
            return self.send(self.upSocket, self.upSocketSendQueue.get())
        return 0
    #
    #
    #
    # downSocket 的方法

    def downSocketRecv(self):
        buff = self.recv(self.downSocket)
        bl = len(buff)
        if self.clientFuckGFW:
            self.clientFuckGFW = False
            self.serverFuckGFW = False
            return bl
        if bl > 0:
            self.downSocketRecvQueue.put(buff)
        return bl

    def serverSocketRecv(self):
        buff = self.recv(self.serverSocket)
        bl = len(buff)
        if bl > 0:
            self.serverSocketRecvQueue.put(buff)
        return bl

    def serverSocketSend(self):
        if self.serverSocketSendQueue.qsize() > 0:
            return self.send(self.serverSocket, self.serverSocketSendQueue.get())
        return 0
