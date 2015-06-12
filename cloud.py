#!/usr/bin/python
import server
import scanner
import worker
import sys

if len(sys.argv) == 1:
    #TODO: write help.txt file
    print('helpstring')
elif sys.argv[1] == 'sys':
    print server.getServerProps()
elif sys.argv[1] == 'run':
    worker.run()
elif sys.argv[1] == 'scan':
    print(scanner.scanCloud())



