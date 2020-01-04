#!/usr/bin/python3
#c =b'\xff\x01'
#print(int.from_bytes(c,'little'))
#a = 5
#print(a.to_bytes(2,'big'))
import socket,select,time

ss = socket.socket()
ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
addr = ('127.0.0.1',8000)
ss.bind(addr)
ss.listen()
cl,ad = ss.accept()
buff = bytes(1024*2)
while True:
    a=len(cl.recv(1024))
    print(a)