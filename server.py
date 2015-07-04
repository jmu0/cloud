import time
import json
import sys
import socket
import hypervisor
import storage
import subprocess


def getCloudPort():
    return 7777


def getServerIP(name):
    return socket.gethostbyname(name)


def getHostName():
    return socket.gethostname()


def getLoadAvg():
    ''' read load average '''
    l = {}
    with open('/proc/loadavg') as f:
        line = f.readline()
    line = line.split()
    l['1'] = line[0]
    l['5'] = line[1]
    l['15'] = line[2]
    l['tasks'] = line[3]
    l['lastProc'] = line[4]
    l['loadLine'] = line[0] + ', ' + line[1] + ', ' + line[2]
    return l


def getServerProps():
    '''get properties of localhost'''
    # TODO: get system load /memory stats
    props = {}
    props['name'] = getHostName()
    props['ip'] = getServerIP(props['name'])
    props['mac'] = 'mac address'
    if hypervisor.isHypervisor():
        props['is_hypervisor'] = 'True'
        props['virsh_version'] = hypervisor.getVirshVersion()
        props['guests'] = hypervisor.getGuestList()
    else:
        props['is_hypervisor'] = 'False'
        props['virsh_version'] = 'not installed'
        props['guests'] = []
    if storage.isNfsServer():
        props['is_nfs_server'] = 'True'
        props['shares'] = storage.getShares()
    else:
        props['is_nfs_server'] = 'False'
        props['shares'] = []
    props['mounts'] = storage.getMounts()
    props['lastPing'] = time.time()
    props['loadavg'] = getLoadAvg()
    props['load'] = props['loadavg']['loadLine']
    return props


def portscan(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.01)
        s.connect((ip, port))
        s.settimeout(None)
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
        s.settimeout(2)
        s.connect((ip, getCloudPort()))
        s.settimeout(None)
        cmd = 'handshake ' + json.dumps(getServerProps())
        # cmd += '\n'
        cmd = cmd.encode()
        s.sendall(cmd)
        data = s.recv(10 * 1024, socket.MSG_WAITALL)
        data = data.decode()
        # print('handshake answer: ' + str(data))
        data = json.loads(data)
        data['lastPing'] = time.time()
        return data
    except:
        print('handshake failed: ' + str(ip) + " "
              + str(sys.exc_info()[1]))
        return False


def getFirstServer():
    '''return ip of first cloud server found'''
    # try localhost
    localip = getServerIP(getHostName())
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

def getMac(hostname):
    try:
        with open(str(sys.path[0]) + '/mac.json') as f:
            js = f.read()
        macs = json.loads(js)
        for key in macs.keys():
            if key == hostname:
                return macs[key]
        return False
    except:
        print(str(sys.exc_info()[1]))
        return False


def wake(hostname):
    mac = getMac(hostname)
    if mac:
        isWol = subprocess.call(['which', 'wol'])
        isWakeOnLan = subprocess.call(['which', 'wakeonlan'])
        if isWol == 0:
            cmd = ['wol', mac]
        elif isWakeOnLan == 0:
            cmd = ['wakeonlan', mac]
        else:
            print('no wake-on-lan package installed')
            return False
        return str(subprocess.check_output(cmd))
