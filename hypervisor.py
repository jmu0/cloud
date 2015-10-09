import os
import socket
import time


def is_hypervisor():
    ''' check if virsh is installed on local server '''
    with os.popen('which virsh') as f:
        version = f.read()[0:-1]
    if len(version) > 0:
        return True
    else:
        return False


def get_virsh_version():
    ''' get local virsh version '''
    if (is_hypervisor()):
        with os.popen('virsh --version') as f:
            version = f.read()[0:-1]
        if len(version) > 0:
            return version
        else:
            return 'not installed'
    else:
        return 'not installed'


def get_guest_list():
    ''' get list of dictionaries containing local guests '''
    # TODO: get disk image location
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
                "host": servername,
                "image_path": get_guest_image_path(l[1])
            }
            list.append(item)
    return list


def has_guest(guest_name):
    ''' check if guest is running on local server '''
    for g in get_guest_list():
        if g['name'] == guest_name:
            return True
    return False


def get_guest_image_path(guest_name):
    ''' get image path for local guest '''
    cmd = 'virsh domblklist ' + guest_name + ' 2> /dev/null'
    with os.popen(cmd) as f:
        txt = f.read()
    txt = txt.split()[4]
    return txt


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


def guest_create(guest_image_path):
    ''' create guest on local server '''
    cmd = "virsh create " + guest_image_path
    print("guest create command: " + str(cmd))
    with os.popen(cmd) as f:
        txt = f.read()[0:-1]
    txt = str(txt)
    if txt == '':
        txt = 'OK'
    print("guest create response: " + txt)
    return txt


def guest_shutdown(guest_name):
    ''' shutdown guest on local server '''
    interval = 0.5   # interval to check if guest is alive in ms
    tests = 10  # number of times to test, then destroy guest
    cmd = "virsh shutdown " + guest_name
    print("guest shutdown command: " + str(cmd))
    with os.popen(cmd) as f:
        txt = f.read()[0:-1]
    txt = str(txt)
    if txt == '':
        txt = 'OK'
    print("guest shutdown response: " + txt)
    for i in range(tests):
        if not has_guest(guest_name):
            # TODO: does not break loop??
            print('guest ' + guest_name + ' has shut down.')
            return txt
            break
        time.sleep(interval)
    return guest_destroy(guest_name)


def guest_destroy(guest_name):
    ''' destroy guest on local server '''
    cmd = "virsh destroy " + guest_name
    print("guest destroy command: " + str(cmd))
    with os.popen(cmd) as f:
        txt = f.read()[0:-1]
    txt = str(txt)
    if txt == '':
        txt = 'OK'
    print("guest destroy response: " + txt)
    return txt
