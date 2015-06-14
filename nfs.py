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
