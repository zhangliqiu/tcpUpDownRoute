#!/usr/bin/python3

from classes import *
from log import *
import time
import socket
import select
import sys
def ck(value,name):
    print('name:    %s value:   %s' % (name,value))
    return value
funMap = {}  # socket 处理方法索引
rlist = []
wlist = []
xlist = []
clientList = []
clientSqu = 0
disSelectEventNum = True
disLists = True
# client or trans  or server
MODE = sys.argv[1]
print('MODE=',MODE)

# client mode need argvs
DownServerAddr = ('127.0.0.1', 50002)
UpServerAddr = ('127.0.0.1', 50001)
clientListenSocketAddr = ('0.0.0.0', 55000)
clientListenSocket = socket.socket()
clientListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# trans mode nedd argvs
transListenDownSocketAddr = ('0.0.0.0', 55001)
transListenDownSocekt = socket.socket()
transListenDownSocekt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# server mode need argvs
serverListenDownSocketAddr = ('0.0.0.0', 50001)
serverListenUpSocketAddr = ('0.0.0.0', 50002)
remoteSocketAddr = ('127.0.0.1', 22)
serverListenUpSocket = socket.socket()
serverListenDownSocket = socket.socket()
serverListenUpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverListenDownSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
modeServerIsClientConnecting = False
# server mode temp var to save the connecting socket
modeServerTempUpSocket = None
modeServerTempDownSocket = None

def sumList():
    return ('rlist:%s     wlist:%s    xlist:%s    funMap:%s'%(len(rlist),len(wlist),len(xlist),len(funMap)))
def listen(sock=socket.socket()):
    sock.listen()
    addr = sock.getsockname()
    log('%s:%s listening...' % (addr[0], addr[1]))


def listenSockPrepare(sock, addr):
    sock.bind(addr)
    listen(sock)
    rlist.append(sock)
    #xlist.append(sock)


def accept(listenSocket=socket.socket()):
    sock, addr = listenSocket.accept()
    log('%s:%s connected' % (addr[0], addr[1]))
    return sock


def connect(sock, addr):
    if sock.connect_ex(addr):
        log('connect %s:%s fail' % (addr[0], addr[1]))
        return False
    return True


def modeClientAccept():  # Client mode to accept a connection and make a client
    acceptSocket = accept(clientListenSocket)
    client = Client()
    client.clientSocket = acceptSocket
    if connect(client.upSocket, UpServerAddr):
        if connect(client.downSocket, DownServerAddr):
            # care about reading event
            rlist.append(client.clientSocket)
            rlist.append(client.upSocket)
            rlist.append(client.downSocket)
            # care about writing event
            wlist.append(client.clientSocket)
            wlist.append(client.upSocket)
            # return the group Client class which active socket
            funMap[client.clientSocket] = client.clientSelf
            funMap[client.upSocket] = client.clientSelf
            funMap[client.downSocket] = client.clientSelf
            # add to clientList
            clientList.append(client)
        else:
            acceptSocket.close()
    else:
        acceptSocket.close()


def modeClientClientDie(client=Client()):  # Client mode to close a client
    rlist.remove(client.clientSocket)
    rlist.remove(client.upSocket)
    rlist.remove(client.downSocket)

    wlist.remove(client.clientSocket)
    wlist.remove(client.upSocket)

    del funMap[client.clientSocket]
    del funMap[client.upSocket]
    del funMap[client.downSocket]
    clientList.remove(client)
    client.closeAllSockets()


def modeTransAccept():  # trans mode to accepte a connection and make a client
    acceptSocekt = accept(transListenDownSocekt)
    client = Client()
    client.downSocket = acceptSocekt
    if connect(client.upSocket, transListenDownSocketAddr):
        # care about reading event
        rlist.append(client.downSocket)
        rlist.append(client.upSocket)
        # care about writing event
        wlist.append(client.upSocket)
        # return the group Client class which active socket
        funMap[client.upSocket] = client.clientSelf
        funMap[client.downSocket] = client.clientSelf
        # add to clientList
        clientList.append(client)


def modeTransClientDie(client=Client()):  # trans mode to close a client
    rlist.remove(client.upSocket)
    rlist.remove(client.downSocket)

    wlist.remove(client.upSocket)

    del funMap[client.upSocket]
    del funMap[client.downSocket]
    clientList.remove(client)
    client.closeAllSockets()


# server mode to  make a client
def modeServerAccept(upSocket=socket.socket(), downSocket=socket.socket()):
    global modeServerIsClientConnecting
    client = Client()
    client.downSocket = downSocket
    client.upSocket = upSocket
    if connect(client.serverSocket, remoteSocketAddr):
        # care about reading event
        rlist.append(client.downSocket)
        rlist.append(client.serverSocket)
        rlist.append(client.upSocket)
        # care about writing event
        wlist.append(client.upSocket)
        wlist.append(client.serverSocket)
        # return the group Client class which active socket
        funMap[client.upSocket] = client.clientSelf
        funMap[client.downSocket] = client.clientSelf
        funMap[client.serverSocket] = client.clientSelf
        # add to clientList
        clientList.append(client)
        modeServerIsClientConnecting = False


def modeServerClientDie(client=Client()):  # trans mode to close a client
    rlist.remove(client.upSocket)
    rlist.remove(client.downSocket)
    rlist.remove(client.serverSocket)

    wlist.remove(client.serverSocket)
    wlist.remove(client.upSocket)

    del funMap[client.upSocket]
    del funMap[client.downSocket]
    del funMap[client.serverSocket]
    clientList.remove(client)
    client.closeAllSockets()

def clientDie(client):
    log('断开前：%s'% sumList())
    if MODE == 'client':
        modeClientClientDie(client)
    elif MODE == 'trans':
        modeTransClientDie(client)
    else:
        modeServerClientDie(client)
    log('断开后：%s'% sumList())

# common mode ,client or trans or server, to dear the event from client
def clientEventResolu(s):
    client = funMap[s]()
    # from client.clientSocket
    if s == client.clientSocket:
        buffsize = client.clientSocketRecv()
        if buffsize == 0:
            clientDie(client)
            return False
    # from client.upSocket
    elif s == client.upSocket:
        buffsize = client.upSocketRecv()
        if buffsize == 0:
            clientDie(client)
            return False
    # from client.downSocket
    elif s == client.downSocket:
        buffsize = client.downSocketRecv()
        if buffsize == 0:
            clientDie(client)
            return False
    elif s == client.serverSocket:
        buffsize = client.serverSocketRecv()
        if buffsize == 0:
            clientDie(client) 
            return False
    return True           

def queueManage(client=Client()):
    if MODE == 'client':
        # client.clientSocketRecvQueue      -->     client.upSocketSendQueue
        # client.downSocketRecvQueue        -->     client.clientSocketSendQueue
        while client.clientSocketRecvQueue.qsize():
            client.upSocketSendQueue.put(client.clientSocketRecvQueue.get())
        while client.downSocketRecvQueue.qsize():
            client.clientSocketSendQueue.put(client.downSocketRecvQueue.get())
    elif MODE == 'trans':
        # client.downSocketRecvQueue        -->     client.upSocketSendQueue
        while client.downSocketRecvQueue.qsize():
            client.upSocketSendQueue.put(client.downSocketRecvQueue.get())
    else:
        # MODE == 'server'
        # client.serverSocketRecvQueue      -->     client.upSocketSendQueue
        # client.downSocketRecvQueue        -->     client.serverSocketSendQueue
        while client.serverSocketRecvQueue.qsize():
            client.upSocketSendQueue.put(client.serverSocketRecvQueue.get())
        while client.downSocketRecvQueue.qsize():
            client.serverSocketSendQueue.put(client.downSocketRecvQueue.get())


def sendData(s):  # common mode , to send all needed to sending
    client = funMap[s]()
    if s == client.clientSocket:
        client.clientSocketSend()
    elif s == client.upSocket:
        client.upSocketSend()
    elif s == client.serverSocket:
        client.serverSocketSend()


if MODE == 'client':
    listenSockPrepare(clientListenSocket, clientListenSocketAddr)
elif MODE == 'trans':
    listenSockPrepare(transListenDownSocekt, transListenDownSocketAddr)
else:
    listenSockPrepare(serverListenUpSocket, serverListenUpSocketAddr)
    listenSockPrepare(serverListenDownSocket, serverListenDownSocketAddr)
ifreSelect = False
while True: 
    rs, ws, es = select.select(rlist, wlist, xlist)   
    
    for s in rs:
        # accept client connect
        # client mode
        if s == clientListenSocket:
            log('连接前：%s'% sumList())
            modeClientAccept()
            log('连接后：%s'% sumList())
        # trans mode
        elif s == transListenDownSocekt:
            modeTransAccept()
        # server mode
        elif s == serverListenUpSocket:
            modeServerTempUpSocket = accept(s)
            if modeServerIsClientConnecting == True:
                log('连接前：%s'% sumList())
                modeServerAccept(modeServerTempUpSocket,
                                 modeServerTempDownSocket)
                log('连接后：%s'% sumList())
            else:
                log('upSocket already connected, waitting for downSocket connectting....')
                modeServerIsClientConnecting = True

        elif s == serverListenDownSocket:
            modeServerTempDownSocket = accept(s)
            if modeServerIsClientConnecting == True:
                modeServerAccept(modeServerTempUpSocket,
                                 modeServerTempDownSocket)
            else:
                log('downSocket already connected, waitting for upSocket connectting....')
                modeServerIsClientConnecting = True
        else:
            # recv the data from client.clientSocket or client.upSocket or client.downSocket
            re = clientEventResolu(s)
            if re == False:
                ifreSelect = True
            if ifreSelect:
                break
    
    if ifreSelect:
        ifreSelect = False
        continue
    for s in ws:   
             
        #log('ws:%s wlist:%s' % (len(ws),len(wlist)))
        client = funMap[s]()
        # queue manage
        queueManage(client)
        # only the client.upSocket ,clientSocket, serverSocket need send data
        sendData(s)
    for s in es:
        pass
    #log('rs:%s ws:%s es:%s rlist:%s wlist:%s xlist:%s' % (len(rs),len(ws),len(es),len(rlist),len(wlist),len(xlist)))
