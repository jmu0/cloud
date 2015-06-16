#!/usr/bin/python3
import scanner
import server
import printer
import sys
import worker

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
        guest = sys.argv[2]
        to_server = sys.argv[3]
        command = 'migrate ' + guest + ' ' + to_server
        resp = scanner.getFromSocket(command)
        print(resp)
    else:
        print('Invalid arguments.')
