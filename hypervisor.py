import os


def isHypervisor():
    version = os.popen('virsh --version').read()[0:-1]
    if len(version) > 0:
        return True
    else:
        return False


def getVirshVersion():
    return os.popen('virsh --version').read()[0:-1]


def getGuestList():
    txt = os.popen('virsh list').read()[0:-1]
    txt = txt.split('\n')[2:]
    list = []
    for l in txt:
        l = l.split()
        if len(l) is 3:
            item = {"id": l[0], "name": l[1], "state": l[2]}
            list.append(item)

    return list
