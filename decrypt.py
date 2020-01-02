#!/usr/bin/python3
import socket
BUFFSIZE = 1024*10
cl = socket.socket()
addr = ('127.0.0.1', 8000)
cl.connect(addr)

def sendToServer(buff):
    ns = cl.send(buff)
    dbuff = cl.recv(BUFFSIZE)
    print('send %s bytes to encrypt andr recv %s bytes'%(ns,len(dbuff)))
    if len(buff)<100:
        print('SDATA:\n%s'% buff)
        print('DDATA:\n%s'% dbuff)
    return dbuff

def encrypt(buff):
    return sendToServer(buff)
def decrypt(buff):
    return sendToServer(buff)
