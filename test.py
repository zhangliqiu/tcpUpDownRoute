#!/usr/bin/python3
#c =b'\xff\x01'
#print(int.from_bytes(c,'little'))
#a = 5
#print(a.to_bytes(2,'big'))
import socket,select,time
from log import *
from queue import Queue
def socketbufftest():
    addr = ('ras.com',4445)
    s = socket.socket()
    s.connect(addr)
    buff = bytes(1024)
    while True:
        rs,ws,es = select.select([],[s],[])
        if ws:
            s.send(buff)
            
       
socketbufftest()

