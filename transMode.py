#!/usr/bin/python3

from classes import *
from log import *
import time
import socket
import select
import sys
import configparser

ifFuckGFW = True

funMap = {}  # socket 处理方法索引
rlist = []
wlist = []
xlist = []
clientList = []
clientSqu = 0
disSelectEventNum = True
disLists = True
# client or trans  or server
if len(sys.argv) != 2 or sys.argv[1] not in ['client', 'trans', 'server']:
    print('usage: %s [client|trans|server]' % sys.argv[0])
    exit()
MODE = sys.argv[1]
print('MODE=', MODE)
config = configparser.ConfigParser()
config.read('config.ini')
di = config._sections

with open('httpRequest','rb') as fl:
    FUCKGFW_CLIENT_SEND = fl.read()
with open('httpRespond','rb') as fl:
    FUCKGFW_SERVER_SEND = fl.read()



# client mode need argvs
DownServerAddr = strAddrToAddr(di['client']['downserveraddr'])
UpServerAddr = strAddrToAddr(di['client']['upserveraddr'])
clientListenSocketAddr = strAddrToAddr(di['client']['clientlistensocketaddr'])
clientListenSocket = socket.socket()
clientListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# trans mode nedd argvs
transListenDownSocketAddr = strAddrToAddr(di['trans']['translistendownsocketaddr'])
transUpSocketAddr = strAddrToAddr(di['trans']['transupsocketaddr'])
transListenDownSocekt = socket.socket()
transListenDownSocekt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# server mode need argvs
serverListenUpSocketAddr = strAddrToAddr(di['server']['serverlistenupsocketaddr'])
serverListenDownSocketAddr = strAddrToAddr(di['server']['serverlistendownsocketaddr'])
# serverListenDownSocketAddr = UpServerAddr
remoteSocketAddr = strAddrToAddr(di['server']['remotesocketaddr'])
serverListenUpSocket = socket.socket()
serverListenDownSocket = socket.socket()
serverListenUpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverListenDownSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
modeServerIsClientConnecting = False
# server mode temp var to save the connecting socket
modeServerTempUpSocket = None
modeServerTempDownSocket = None




def sumList():
    print ('rlist:%s     wlist:%s    xlist:%s    funMap:%s' % (len(rlist), len(wlist), len(xlist), len(funMap)))


def listen(sock=socket.socket()):
    sock.listen()
    addr = sock.getsockname()
    log('%s:%s listening...' % (addr[0], addr[1]))


def listenSockPrepare(sock, addr):
    sock.bind(addr)
    listen(sock)
    rlist.append(sock)
    # xlist.append(sock)


def accept(listenSocket):
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
            #fuck GFW
            client.mode = 'client'
            client.downSocket.send(FUCKGFW_CLIENT_SEND)
            client.downSocket.recv(BUFFSIZE)
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
            client.lastPrintSpeedTime = time.time()
            clientList.append(client)
        else:
            acceptSocket.close()
    else:
        acceptSocket.close()


def modeClientClientDie(client):  # Client mode to close a client
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
    if connect(client.upSocket, transUpSocketAddr):
        # care about reading event
        client.mode = 'trans'
        rlist.append(client.downSocket)
        rlist.append(client.upSocket)
        # care about writing event
        wlist.append(client.upSocket)
        # return the group Client class which active socket
        funMap[client.upSocket] = client.clientSelf
        funMap[client.downSocket] = client.clientSelf
        # add to clientList
        client.lastPrintSpeedTime = time.time()
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
def modeServerAccept(upSocket, downSocket):
    global modeServerIsClientConnecting
    client = Client()
    client.downSocket = downSocket
    client.upSocket = upSocket
    # client.serverFuckGFW = True
    client.upSocket.recv(BUFFSIZE)
    client.upSocket.send(FUCKGFW_SERVER_SEND)
    if connect(client.serverSocket, remoteSocketAddr):
        client.mode = 'server'
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
        client.lastPrintSpeedTime = time.time()
        clientList.append(client)
        modeServerIsClientConnecting = False
    else:
        client.closeAllSockets()


def modeServerClientDie(client):  # trans mode to close a client
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
    #log('断开前：%s' % sumList())
    if MODE == 'client':
        modeClientClientDie(client)
    elif MODE == 'trans':
        modeTransClientDie(client)
    else:
        modeServerClientDie(client)
    #log('断开后：%s' % sumList())

# common mode ,client or trans or server, to dear the event from client


def clientEventResolu(s):
    client = funMap[s]()
    # from client.clientSocket
    if s == client.clientSocket:
        buffsize = client.clientSocketRecv()
        if buffsize == -1:
            clientDie(client)
            return False
    # from client.upSocket
    elif s == client.upSocket:
        buffsize = client.upSocketRecv()
        if buffsize == -1:
            clientDie(client)
            return False
    # from client.downSocket
    elif s == client.downSocket:
        buffsize = client.downSocketRecv()
        if buffsize == -1:
            clientDie(client)
            return False
    elif s == client.serverSocket:
        buffsize = client.serverSocketRecv()
        if buffsize == -1:
            clientDie(client)
            return False
    return True


def queueManage(client,s):
    if MODE == 'client':
        # client.clientSocketRecvBuff      -->     client.upSocketSendBuff
        # client.downSocketRecvBuff        -->     client.clientSocketSendBuff
        if client.clientSocket == s:
            client.clientSocketSendBuff = client.downSocketRecvBuff
            client.downSocketRecvBuff = b''
        if client.upSocket == s:
            client.upSocketSendBuff = client.clientSocketRecvBuff
            client.clientSocketRecvBuff = b''
    elif MODE == 'trans':
        # client.downSocketRecvBuff        -->     client.upSocketSendBuff
        if client.upSocket == s:
            client.upSocketSendBuff = client.downSocketRecvBuff
            client.downSocketRecvBuff = b''
    else:
        # MODE == 'server'
        # client.serverSocketRecvBuff      -->     client.upSocketSendBuff
        # client.downSocketRecvBuff        -->     client.serverSocketSendBuff
        if client.upSocket == s:
            client.upSocketSendBuff = client.serverSocketRecvBuff
            client.serverSocketRecvBuff = b'' 
        if client.serverSocket == s:
            client.serverSocketSendBuff = client.downSocketRecvBuff
            client.downSocketRecvBuff = b''   


def sendData(client,s):  # common mode , to send all needed to sending
    
    if s == client.clientSocket:
        now = time.time()
        tt = now - client.lastPrintSpeedTime
        if tt > 2:
            speed = client.transDataSize / 2 / 1024
            if speed > 10:
                log('%s kb/s' % int(speed),True,True)
            client.transDataSize = 0
            client.lastPrintSpeedTime = now

        client.transDataSize += client.clientSocketSend()       
    elif s == client.upSocket:
        client.upSocketSend()
    elif s == client.serverSocket:
        client.serverSocketSend()

def strSpeedTofloat(strSpeed=''):  
    speed = float(strSpeed.replace('k',''))
    speed *= 1.3
    timesleep = 1/speed  
    print(timesleep)  
    return timesleep
if MODE == 'client':
    listenSockPrepare(clientListenSocket, clientListenSocketAddr)    
    sleepTime = strSpeedTofloat(di['client']['speed'])
elif MODE == 'trans':
    listenSockPrepare(transListenDownSocekt, transListenDownSocketAddr)
    sleepTime = strSpeedTofloat(di['trans']['speed'])
else:
    listenSockPrepare(serverListenUpSocket, serverListenUpSocketAddr)
    log('serverListenUpSocketAddr %s' % serverListenUpSocketAddr.__str__())
    listenSockPrepare(serverListenDownSocket, serverListenDownSocketAddr)
    log('serverListenDownSocketAddr %s' % serverListenDownSocketAddr.__str__())
    sleepTime = strSpeedTofloat(di['server']['speed'])
ifreSelect = False
while True:
    rs, ws, es = select.select(rlist, wlist, xlist)
    for s in rs:
        # accept client connect
        # client mode
        if s == clientListenSocket:
            #log('连接前：%s' % sumList())
            modeClientAccept()
            #log('连接后：%s' % sumList())
        # trans mode
        elif s == transListenDownSocekt:
            modeTransAccept()
        # server mode
        elif s == serverListenUpSocket:
            modeServerTempUpSocket = accept(s)
            if modeServerIsClientConnecting == True:
                #log('连接前：%s' % sumList())
                modeServerAccept(modeServerTempUpSocket,
                                 modeServerTempDownSocket)
                #log('连接后：%s' % sumList())
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
        sumList()
        continue
    for s in ws:

        #log('ws:%s wlist:%s' % (len(ws),len(wlist)))
        client = funMap[s]()
        # queue manage
        queueManage(client,s)
        # only the client.upSocket ,clientSocket, serverSocket need send data
        sendData(client,s)
    for s in es:
        pass
    time.sleep(sleepTime)
