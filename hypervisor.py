import os
import socket

# TODO: balance load between hypervisors??


def isHypervisor():
    with os.popen('which virsh') as f:
        version = f.read()[0:-1]
    if len(version) > 0:
        return True
    else:
        return False


def getVirshVersion():
    if (isHypervisor()):
        with os.popen('virsh --version') as f:
            version = f.read()[0:-1]
        if len(version) > 0:
            return version
        else:
            return 'not installed'
    else:
        return 'not installed'


def getGuestList():
    servername = socket.gethostname()
    with os.popen('virsh list 2> /dev/null') as f:
        txt = f.read()[0:-1]
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


def guest_migrate(guest_name, to_server_name):
    ''' migrate guest to server '''
    cmd = "virsh migrate --live --unsafe " + guest_name
    cmd += " qemu+tcp://" + to_server_name + "/system"
    print("migrate command: " + str(cmd))
    with os.popen(cmd) as f:
        txt = f.read()[0:-1]
    txt = str(txt)
    if txt == '':
        txt = 'OK'
    print("migrate response: " + txt)
    return txt


def guest_create(guest_name, on_server_name):
    ''' create guest on server '''
    pass


def guest_shutdown(guest_name):
    ''' shutdown guest '''
    pass


def guest_destroy(guest_name):
    ''' destroy guest '''
    pass
