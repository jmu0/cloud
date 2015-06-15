import socket
import json
import server


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
    return found


def scanCloud():
    ips = scanNetwork(getCloudPort())
    cloud = []
    # print(ips)
    for ip in ips:
        print('scanning ' + ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, getCloudPort()))
        cmd = 'handshake ' + json.dumps(server.getServerProps())
        cmd = cmd + '\n'
        cmd = cmd.encode()
        s.send(cmd)
        data = b''
        while True:
            buf = s.recv(1024)
            data += buf
            # if not buf or str(buf).find('\n'):
            if not buf:
                break
        try:
            data = data.decode()
            data = json.loads(data)
            cloud.append(data)
        except:
            print('Cannot decode json: ' + str(data))
            pass
    return cloud


def getFirstServer():
    '''return ip of first cloud server found'''
    # try localhost
    localip = server.getServerIP(server.getHostName())
    port = getCloudPort()
    if portscan(localip, port):
        return localip
    # scan network, return first found server
    for x in range(0, 256):
        ip = "10.0.0." + str(x)
        if ip != localip:
            if portscan(ip, port):
                return ip
    return False


def getFromSocket(command):
    '''get data from running cloud instance'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = getFirstServer()
    if (ip):
        s.connect((ip, getCloudPort()))
        cmd = command
        cmd = cmd.encode()
        s.send(cmd)
        data = b''
        while True:
            buf = s.recv(1024)
            data += buf
            # if not buf or str(buf).find('\n'):
            if not buf:
                break
        try:
            data = data.decode()
            data = json.loads(data)
            return data
        except:
            print('Cannot decode json: ' + str(data))
            return False
    else:
        return False


def getServers():
    return getFromSocket('servers')


def getGuests():
    return getFromSocket('guests')


def getShares():
    return getFromSocket('shares')


def getMounts():
    return getFromSocket('mounts')
