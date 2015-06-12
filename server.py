import socket
import sys
import json
import hypervisor
import scanner

def getServerIP(name):
    return socket.gethostbyname(name)

def getHostName():
    return socket.gethostname()

def getServerProps():
    props = {};
    props['name'] = getHostName()
    props['ip'] = getServerIP(props['name'])
    props['mac'] = 'mac address'
    if hypervisor.isHypervisor():
        props['is_hypervisor'] = True
        props['virsh_version'] = hypervisor.getVirshVersion()
        props['guests'] = hypervisor.getGuestList()
    else:
        props['is_hypervisor'] = False
    print(props)
    return props

