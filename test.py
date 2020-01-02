#!/usr/bin/python3
#c =b'\xff\x01'
#print(int.from_bytes(c,'little'))
#a = 5
#print(a.to_bytes(2,'big'))
import socket,select,time

ss = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
addr = ('127.0.0.1',8000)
buff = bytes(1024*2)
ss.sendto(buff,0,addr)
data,addr = ss.recvfrom(1024*1024)
print(data)