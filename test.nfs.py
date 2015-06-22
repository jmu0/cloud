#!/usr/bin/python3
import nfs

# shares = nfs.getShares()
# print(shares)
prim = {
    'name': 'pxe',
    'network': '10.0.0.1/24',
    'path': '/nfs/pxe',
    'server': 'mediaserver'
}
sec = {
    'name': 'pxe',
    'network': '10.0.0.1/24',
    'path': '/nfs/pxe',
    'server': 'cloud01'
}
print(prim)
print(sec)
print(nfs.syncShare(prim, sec))
