#!/usr/bin/python3
import server
import storage
import printer
import sys
import worker
import os
import time


os.environ['PYTHONUNBUFFERED'] = 'True'  # for redirecting stdout to log file


def getServers():
    return server.getFromSocket('servers')


def getGuests():
    return server.getFromSocket('guests')


def getShares():
    return server.getFromSocket('shares')


def getMounts():
    return server.getFromSocket('mounts')


if len(sys.argv) == 1:
    # TODO: write help.txt file
    print('helpstring')
elif sys.argv[1] == 'sys':
    start = time.time()
    print(server.getServerProps())
    print(str(time.time() - start) + ' seconds')
elif sys.argv[1] == 'run':
    worker.run()
elif sys.argv[1] == 'scan':
    print(server.scanCloud())
elif sys.argv[1] == 'servers':
    printer.printServerList(getServers())
elif sys.argv[1] == 'guests':
    printer.printGuestList(getGuests())
elif sys.argv[1] == 'shares':
    printer.printShareList(getShares())
elif sys.argv[1] == 'mounts':
    printer.printMountList(getMounts())
elif sys.argv[1] == 'migrate':
    if len(sys.argv) == 4:
        ''' migrate guest to server'''
        guest = sys.argv[2]
        to_server = sys.argv[3]
        command = 'cmd {"action":"migrate","guest":"' + guest
        command += '","to_server":"' + to_server + '"}'
        resp = server.getFromSocket(command)
        print(resp)
    elif len(sys.argv) == 5 and sys.argv[2] == 'all':
        ''' migrate all '''
        from_server = sys.argv[3]
        to_server = sys.argv[4]
        command = 'cmd {"action":"migrateAll","from_server":"' + from_server
        command += '","to_server":"' + to_server + '"}'
        resp = server.getFromSocket(command)
        print(resp)
    else:
        print('Invalid arguments.')
elif sys.argv[1] == 'share':
    # TODO: move this to worker (see migrate)
    if len(sys.argv) == 3:
        print(storage.createShare(sys.argv[2]))
    else:
        print('Invalid arguments.')
elif sys.argv[1] == 'mount':
    # TODO: move this to worker (see migrate)
    if len(sys.argv) == 3:
        shares = getShares()
        m_share = False
        for share in shares:
            s = share['server'] + ':' + share['path']
            if s == sys.argv[2]:
                m_share = share
        print(storage.mount(m_share))
    else:
        print('Invalid arguments.')
elif sys.argv[1] == 'move':
    # TODO: move guest
    pass
elif sys.argv[1] == 'stop':
    # TODO: stop guest
    pass
elif sys.argv[1] == 'destroy':
    # TODO: destroy guest
    pass
