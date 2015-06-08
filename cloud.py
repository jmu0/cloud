#!/usr/bin/python
import socket
import json

class server:
    info = []
    def __init__(self):
        self.info.name = socket.gethostname()
        self.info.ip = socket.gethostbyname(self.name)
    
    def getVars(self):
        return json.dumps(self.info)


s = server()
print s.getVars()
    
