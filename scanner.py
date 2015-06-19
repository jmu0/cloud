import socket
import json
import server
import time
import sys


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
        srv = handshake(ip)
        if (srv):
            cloud.append(srv)
    return cloud


def handshake(ip):
    ''' send handshake '''
    # print('handshake to: ' + ip)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
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
        print('handshake failed: ' + str(ip) + "err: " + sys.exc_info()[0])
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


def getFromSocket(command='', ip=None):
    '''get data from running cloud instance'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not ip:
        ip = getFirstServer()
    # print(ip)

    if (ip):
        s.connect((ip, getCloudPort()))
        cmd = command
        cmd = cmd.encode()
        s.sendall(cmd)
        data = s.recv(10 * 1024, socket.MSG_WAITALL)
        # data = b''
        # while True:
        #     buf = s.recv(1024)
        #     data += buf
        #     # if not buf or str(buf).find('\n'):
        #     if not buf:
        #         break
        try:
            data = data.decode()
            # print('length: ' + str(len(data)))
            data = json.loads(data)
            return data
        except:
            print('Response: ' + str(data))
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
