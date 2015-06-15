import socket
import json
import server
import time


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
        cloud.append(handshake(ip))
    return cloud


def handshake(ip):
    print('handshake to: ' + ip)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((ip, getCloudPort()))
        cmd = 'handshake ' + json.dumps(server.getServerProps())
        # cmd += '\n'
        cmd = cmd.encode()
        s.sendall(cmd)
        data = s.recv(5120)
        data = data.decode()
        data = json.loads(data)
        data['lastPing'] = time.time()
        return data
    except:
        print('handshake failed: ' + str(ip))
        return False


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
    print(ip)

    if (ip):
        s.connect((ip, getCloudPort()))
        cmd = command
        cmd = cmd.encode()
        s.send(cmd)
        data = s.recv(5 * 1024)
        # data = b''
        # while True:
        #     buf = s.recv(1024)
        #     data += buf
        #     # if not buf or str(buf).find('\n'):
        #     if not buf:
        #         break
        try:
            data = data.decode()
            print('length: ' + str(len(data)))
            data = json.loads(data)
            return data
        except:
            print('Cannot decode json: ' + str(data))
            print('length: ' + str(len(data)))
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
