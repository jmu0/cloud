import os
import sys
import socket
import subprocess


def isNfsServer():
    return os.path.isfile('/etc/exports')


def getShares():
    f = open('/etc/exports', 'r')
    exportsfile = f.readlines()
    f.close()
    exports = []
    for line in exportsfile:
        share = lineToShare(line)
        if share:
            exports.append(share)
    return exports


def getMounts():
    mounts = []
    f = os.popen('df -h -t nfs 2> /dev/null')
    lines = f.read()
    lines = str(lines).splitlines()[1:]
    f.close()
    servername = socket.gethostname()
    for line in lines:
        line = line.split()
        server = line[0].split(':')
        path = server[1]
        server = server[0]
        name = path.split('/')[-1:][0]
        mount = {
            'mount': line[0],
            'shareserver': server,
            'sharepath': path,
            'sharename': name,
            'server': servername,
            'size': line[1],
            'used': line[2],
            'available': line[3],
            'usedPerc': line[4],
            'mountpoint': line[5]
        }
        mounts.append(mount)
    return mounts


def lineToShare(line):
    if not line.strip()[0] == '#':
        servername = socket.gethostname()
        line = line.split()
        path = line[0]
        name = path.split('/')[-1:][0]
        options = line[1].split('(')
        network = options[0]
        options = options[1]
        options = options[:-1]
        options = options.split(',')
        share = {
            'name': name,
            'path': path,
            'network': network,
            'options': options,
            'server': servername
        }
        return share
    else:
        return False


def shareToLine(share):
    # TODO: create /etc/exports line from share
    pass


def check_if_mounted(mountpoint):
    ''' check if mountpoint is mounted '''
    mounts = getMounts()
    servername = socket.gethostname()
    for m in mounts:
        if m['mountpoint'] == mountpoint and m['server'] == servername:
            return True
    return False


def mount(share):
    ''' mount share '''
    mountpoint = '/mnt/'
    mountpoint += share['server'] + '/'
    mountpoint += share['name']
    # print(mountpoint)
    if not check_if_mounted(mountpoint):
        # print('not mounted')
        sharepath = share['server'] + ':' + share['path']
        # print(sharepath)
        if not os.path.isdir(mountpoint):
            # print('create path' + str(mountpoint))
            cmd = ['mkdir', '-p', mountpoint]
            res = subprocess.call(cmd)
            if not res == 0:
                print('could not create mountpoint')
                print(str(sys.exc_info()[1]))
                return False
        cmd = ['mount', sharepath, mountpoint]
        # print('mounting')
        res = subprocess.call(cmd)
        if not res == 0:
            print('could not mount share')
            print(str(sys.exc_info()[1]))
            return False
        else:
            return True
    else:
        return True


def createShare(path):
    ''' create share from path '''
    # TODO: create share
    pass


def syncShare(share_name):
    ''' sync primary share to secondary shares '''
    # TODO: sync share
    pass


def migrateShare(share_name, to_server):
    ''' migrate share to server (sync, set primary) '''
    # TODO: sync share
    pass
# arch: enable * start rpcbind.service + nfs-server.service
# exportfs -rav
# /nfs/test 10.0.0.1/24(rw,sync,subtree_check,no_root_squash)
