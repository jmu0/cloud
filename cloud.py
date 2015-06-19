#!/usr/bin/python3
import scanner
import server
import printer
import sys
import worker
import os


os.environ['PYTHONUNBUFFERED'] = 'True' # for redirecting stdout to log file


if len(sys.argv) == 1:
    # TODO: write help.txt file
    print('helpstring')
elif sys.argv[1] == 'sys':
    print(server.getServerProps())
elif sys.argv[1] == 'run':
    worker.run()
elif sys.argv[1] == 'scan':
    print(scanner.scanCloud())
elif sys.argv[1] == 'servers':
    printer.printServerList(scanner.getServers())
elif sys.argv[1] == 'guests':
    printer.printGuestList(scanner.getGuests())
elif sys.argv[1] == 'shares':
    printer.printShareList(scanner.getShares())
elif sys.argv[1] == 'mounts':
    printer.printMountList(scanner.getMounts())
elif sys.argv[1] == 'migrate':
    if len(sys.argv) == 4:
        ''' migrate guest to server'''
        guest = sys.argv[2]
        to_server = sys.argv[3]
        command = 'cmd {"action":"migrate","guest":"' + guest + '","to_server":"' + to_server + '"}'
        resp = scanner.getFromSocket(command)
        print(resp)
    elif len(sys.argv) == 5 and sys.argv[2] == 'all':
        ''' migrate all '''
        from_server = sys.argv[3]
        to_server = sys.argv[4]
        command =  'cmd {"action":"migrateAll","from_server":"' + from_server
        command += '","to_server":"' + to_server + '"}'
        resp = scanner.getFromSocket(command)
        print(resp)
    else:
        print('Invalid arguments.')
