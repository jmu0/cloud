import os
import socket


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

# arch: enable * start rpcbind.service + nfs-server.service
# exportfs -rav
# /nfs/test 10.0.0.1/24(rw,sync,subtree_check,no_root_squash)
