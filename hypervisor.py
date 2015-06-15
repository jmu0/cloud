import os
import socket


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
        if len(version) > 0:
            return version
        else:
            return 'not installed'
    else:
        return 'not installed'


def getGuestList():
    servername = socket.gethostname()
    f = os.popen('virsh list')
    txt = f.read()[0:-1]
    f.close()
    txt = txt.split('\n')[2:]
    list = []
    for l in txt:
        l = l.split()
        if len(l) is 3:
            item = {
                "id": l[0],
                "name": l[1],
                "state": l[2],
                "host": servername
            }
            list.append(item)
    return list


def migrate(guest_name, to_server_name):
    cmd = "virsh migrate --live --unsafe" + guest_name
    cmd += " qemu+ssh://" + to_server_name + "/system"
    print("migrate command: " + str(cmd))
    f = os.popen(cmd)
    txt = f.read()[0:-1]
    f.close()
    print("migrate response: " + str(txt))
    return txt
