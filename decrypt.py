#!/usr/bin/python3
import time
key = b'ddfasfasdfasd'
lenKey = len(key)
def encrypt(data):
    edata = b''
    n = 0
    cc = {}
    for t in data:
        
        n += 1

    

def decrypt(data):
    pass
        
mm = 1024*1024
data = bytes(mm)
now=time.time()
kn = 0
edata = {}
for i in range(0,len(data)):
    if kn == lenKey:
        kn = 0
    cc = data[i]^key[kn]
    kn += 1
    edata[i]=cc
t = time.time() - now
print(t)

