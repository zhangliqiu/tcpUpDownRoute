#!/usr/bin/python3
import socket,select
sl = socket.socket()
addr = ('0.0.0.0',22005)
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
                print('from %s recv %s bytes' % (ad.__str__(),bl))
                #s.send(buff)