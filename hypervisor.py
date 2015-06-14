import os


def isHypervisor():
    f = os.popen('which virsh')
    version = f.read()[0:-1]
    f.close()
    if len(version) > 0:
        return True
    else:
        return False


def getVirshVersion():
    if (isHypervisor()):
        f = os.popen('virsh --version')
        version = f.read()[0:-1]
        f.close()
        print('version: ' + str(version))
        if len(version) > 0:
            return version
        else:
            return 'not installed'
    else:
        return 'not installed'


def getGuestList():
    f = os.popen('virsh list')
    txt = f.read()[0:-1]
    f.close()
    txt = txt.split('\n')[2:]
    list = []
    for l in txt:
        l = l.split()
        if len(l) is 3:
            item = {"id": l[0], "name": l[1], "state": l[2]}
            list.append(item)
    return list
