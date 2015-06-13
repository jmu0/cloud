import socket
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
    found = []
    localip = socket.gethostbyname(socket.gethostname())
    for x in range(0, 256):
        ip = "10.0.0." + str(x)
        if ip != localip:
            if portscan(ip, port):
                found.append(ip)
        else:
            print('Not scanning local ip: ' + str(localip))
    return found


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
            buf = s.recv(1024)
            buf = buf.decode()
            data += str(buf)
            if not buf or buf.find('\n'):
                break
        try:
            data = pickle.loads(data)
        except:
            print('Cannot decode pickle: ' + str(data))
            pass
        cloud.append(data)
    return cloud
