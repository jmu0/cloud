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
