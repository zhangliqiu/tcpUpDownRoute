import socket,select
ss = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
ss.bind(('127.0.0.1',55660))
while True:
    data,addr = ss.recvfrom(1024)
    print('from %s:%s recv %s bytes'%(addr[0],addr[1],len(data)))
    ss.sendto(b'ddfa',0,('127.0.0.1',8000))