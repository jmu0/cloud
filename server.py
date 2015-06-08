import socket
import json

#niet gebruikt!!

class server:
    props = {}
    def __init__(self):
        self.props['name'] = socket.gethostname()
        self.props['ip'] = socket.gethostbyname(self.props['name']) 
    
    def getProperties(self):
        return json.dumps(self.props)
