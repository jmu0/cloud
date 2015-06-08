#!/usr/bin/python
import hypervisor
import socket

def getServerProps():
    props = {};
    props['name'] = socket.gethostname()
    props['ip'] = socket.gethostbyname(props['name'])
    if hypervisor.isHypervisor():
        props['is_hypervisor'] = True
        props['virsh_version'] = hypervisor.getVirshVersion()
        props['guests'] = hypervisor.getGuestList()
    else:
        props['is_hypervisor'] = False
    return props

    
print getServerProps()
