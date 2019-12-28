#!/usr/bin/python3
import socket,time
addr = ('0.0.0.0',50000)
listenSocket = socket.socket()
listenSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
listenSocket.bind(addr)
listenSocket.listen()
print('监听',addr)
client,addr = listenSocket.accept()