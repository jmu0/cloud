#!/usr/bin/python

# import hypervisor

# name = 'debian7'
# path = '/var/lib/libvirt/images/debian7.xml'
# hypervisor.guest_create(path)
# print(hypervisor.guest_shutdown(name))
# hypervisor.guest_destroy(name)
# print(hypervisor.has_guest(name))

import storage

s = storage.get_shares()
print(s[1]['meta']['type'])
