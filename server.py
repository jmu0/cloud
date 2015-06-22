import time
import socket
import hypervisor
import nfs


def getServerIP(name):
    return socket.gethostbyname(name)


def getHostName():
    return socket.gethostname()


def getLoadAvg():
    ''' read load average '''
    l = {}
    with open('/proc/loadavg') as f:
        line = f.readline()
    line = line.split()
    l['1'] = line[0]
    l['5'] = line[1]
    l['15'] = line[2]
    l['tasks'] = line[3]
    l['lastProc'] = line[4]
    return l


def getServerProps():
    '''get properties of localhost'''
    # TODO: get system load /memory stats
    props = {}
    props['name'] = getHostName()
    props['ip'] = getServerIP(props['name'])
    props['mac'] = 'mac address'
    if hypervisor.isHypervisor():
        props['is_hypervisor'] = 'True'
        props['virsh_version'] = hypervisor.getVirshVersion()
        props['guests'] = hypervisor.getGuestList()
    else:
        props['is_hypervisor'] = 'False'
        props['virsh_version'] = 'not installed'
        props['guests'] = []
    if nfs.isNfsServer():
        props['is_nfs_server'] = 'True'
        props['shares'] = nfs.getShares()
    else:
        props['is_nfs_server'] = 'False'
        props['shares'] = []
    props['mounts'] = nfs.getMounts()
    props['lastPing'] = time.time()
    props['loadavg'] = getLoadAvg()

    return props
