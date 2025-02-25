#!/usr/bin/python3
import socket
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
di = config._sections
encryPort = int(di['encry']['port'])


BUFFSIZE = 1024*10
addr = ('127.0.0.1', encryPort)
cl = socket.socket()
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
