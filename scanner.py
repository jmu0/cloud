import socket
import time
import pickle 

def getCloudPort(): 
    return 7777

def portscan(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.01)
        s.connect((ip, port))
        s.close()
        return True
    except:
        s.close()
        return False

def scanNetwork(port):
    gevonden = []
    for x in range(0,256):
        ip = "10.0.0." + str(x)
        # print "scanning: " + ip
        if portscan(ip, port):
            # print 'Port ' + str(port) + 'is open op ip:' + ip
            gevonden.append(ip)
    return gevonden

def scanCloud():
    ips = scanNetwork(getCloudPort())
    cloud = []
    print(ips)
    for ip in ips:
        print('scanning ' + ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, getCloudPort()))
        s.send(str.encode('sys'))
        data = ""
        while True:
            buf =  s.recv(1024)
            data += buf
            if not buf or buf.find('\n'): break
        data = data.decode()
        try:
            print(data)
            data = pickle.load(data)
            print(data)
            cloud.push(data)
        except:
            print('cannot decode pickle::' + str(data))
            pass
    return cloud



        

