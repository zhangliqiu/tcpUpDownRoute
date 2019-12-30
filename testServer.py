#!/usr/bin/python3
import socket,select
from log import log
sl = socket.socket()
addr = ('0.0.0.0',4445)

sl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sl.bind(addr)
sl.listen()
print(addr,'listening ')
rlist = [sl]
while True:
    rs,ws,es = select.select(rlist,[],[])
    for s in rs:
        if s == sl:
            cs,ad = sl.accept()
            print(ad,'connected')
            rlist.append(cs)
        else:
            buff = s.recv(1024)
            ad = s.getpeername()
            bl = len(buff)
            if bl == 0:
                print(ad,'disconnected')
                s.close()
                rlist.remove(s)
            else:
                #log('from %s recv %s bytes' % (ad.__str__(),bl))
                print(buff)
                #s.send(buff)