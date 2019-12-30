import time


def strToFile(mes):
    with open('log.log', 'a') as fl:
        fl.write(mes)


def log(mes, isdis=True, toFile=False):
    now = time.asctime(time.localtime())
    if isdis:
        print('%s   %s' % (now, mes))
    if toFile:
        strToFile('%s   %s\n' % (now ,mes))


def ck(value, name):
    print('name:    %s value:   %s' % (name, value))
    return value


def strAddrToAddr(strAddr):
    strAddrArray = strAddr.split()
    if len(strAddrArray) != 2:
        print('strAddrAddray format error')
        exit()
    return (strAddrArray[0], int(strAddrArray[1]))
