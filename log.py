import time
def log(mes,isdis = True):
    now = time.asctime(time.localtime())
    if isdis:
        print('%s   %s' % (now, mes))
