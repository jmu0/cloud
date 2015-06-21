#!/usr/bin/python3
import nfs

# shares = nfs.getShares()
# print(shares)
share = {
    'name': 'plex',
    'network': '10.0.0.1/24',
    'path': '/nfs/plex',
    'server': 'mediaserver'
}
print(nfs.mount(share))
