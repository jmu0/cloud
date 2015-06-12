#!/usr/bin/python
import server
import sys
import scan

if len(sys.argv) == 1:
    #print help string
    #TODO: write help.txt file
    print('helpstring')
elif sys.argv[1] == 'sys':
    #print system properties and exit
    print server.getServerProps()
elif sys.argv[1] == 'run':
    #TODO: run daemon
    pass
elif sys.argv[1] == 'ping':
    #TODO: find other servers (portscan), print and exit
    print(scan.scanNetwork(22))



