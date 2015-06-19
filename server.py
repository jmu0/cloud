import time
import socket
import hypervisor
import nfs

def getServerIP(name):
    return socket.gethostbyname(name)


def getHostName():
    return socket.gethostname()


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
    return props
