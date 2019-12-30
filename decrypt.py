#!/usr/bin/python3

from cryptography.fernet import Fernet
key = b'OJ6koNlaMwsmg9jT3_JzH3mMvur00lbAXEv1Kfkt1D8='
data = b'OJ6koNlaMwsmg9jT3dfadsfasdfa_JzH3mMvur00lbAXEv1Kfkt1D8='
f = Fernet(key)
e_data = f.encrypt(data)
f.decrypt(e_data)