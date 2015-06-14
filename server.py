import socket
import hypervisor


def getServerIP(name):
    return socket.gethostbyname(name)


def getHostName():
    return socket.gethostname()


def getServerProps():
    '''get properties of localhost'''
    props = {}
    props['name'] = getHostName()
    props['ip'] = getServerIP(props['name'])
    props['mac'] = 'mac address'
    if hypervisor.isHypervisor():
        props['is_hypervisor'] = True
        props['virsh_version'] = hypervisor.getVirshVersion()
        props['guests'] = hypervisor.getGuestList()
    else:
        props['is_hypervisor'] = False
        props['virsh_version'] = 'not installed'
        props['guests'] = []
    return props
