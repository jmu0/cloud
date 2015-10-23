import time
import json
import sys
import socket
import hypervisor
import storage
import subprocess


def get_cloud_port():
    return 7777


def get_server_ip(name):
    return socket.gethostbyname(name)


def get_hostname():
    return socket.gethostname()


def get_load_avg():
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


def get_server_props():
    '''get properties of localhost'''
    # TODO: get memory stats
    props = {}
    props['name'] = get_hostname()
    props['ip'] = get_server_ip(props['name'])
    props['mac'] = 'mac address'
    if hypervisor.is_hypervisor():
        props['is_hypervisor'] = 'True'
        props['virsh_version'] = hypervisor.get_virsh_version()
        props['guests'] = hypervisor.get_guest_list()
    else:
        props['is_hypervisor'] = 'False'
        props['virsh_version'] = 'not installed'
        props['guests'] = []
    if storage.is_nfs_server():
        props['is_nfs_server'] = 'True'
        props['shares'] = storage.get_shares()
    else:
        props['is_nfs_server'] = 'False'
        props['shares'] = []
    props['mounts'] = storage.get_mounts()
    props['lastPing'] = time.time()
    props['loadavg'] = get_load_avg()
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


def scan_network(port):
    found = []
    localip = socket.gethostbyname(socket.gethostname())
    for x in range(0, 256):
        ip = "10.0.0." + str(x)
        if ip != localip:
            if portscan(ip, port):
                found.append(ip)
    return found


def scan_cloud():
    ips = scan_network(get_cloud_port())
    cloud = []
    # print(ips)
    for ip in ips:
        srv = handshake(ip)
        if (srv):
            cloud.append(srv)
    return cloud


def handshake(ip):
    ''' send handshake '''
    print('handshake to: ' + ip)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, get_cloud_port()))
        s.settimeout(None)
        cmd = 'handshake ' + json.dumps(get_server_props())
        cmd += '\n'
        cmd = cmd.encode()
        s.sendall(cmd)
        while '\n' not in data:
            print('receiving')
            tmp = s.recv()
            data += tmp.decode()
        # data = s.recv(20 * 1024, socket.MSG_WAITALL)
        if '\n' in data: 
            data = data[:-1]
        data = data.decode()
        s.close()
        print('handshake answer: ' + len(str(data)))
        data = json.loads(data)
        data['lastPing'] = time.time()
        return data
    except:
        print('handshake failed: ' + str(ip) + " "
              + str(sys.exc_info()[1]))
        return False


def get_first_server():
    '''return ip of first cloud server found'''
    # try localhost
    localip = get_server_ip(get_hostname())
    port = get_cloud_port()
    if portscan(localip, port):
        return localip
    # scan network, return first found server
    for x in range(0, 256):
        ip = "10.0.0." + str(x)
        if ip != localip:
            if portscan(ip, port):
                return ip
    return False


def get_from_socket(command='', ip=None):
    '''get data from running cloud instance'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not ip:
        ip = get_first_server()
    # print(ip)

    if (ip):
        s.connect((ip, get_cloud_port()))
        cmd = command
        cmd += '\n'
        cmd = cmd.encode()
        s.sendall(cmd)
        data = s.recv(20 * 1024, socket.MSG_WAITALL)
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
            if '\n' in data:
                data = data[:-1]
            data = json.loads(data)
            return data
        except:
            print('Response: ' + str(data))
            print('length: ' + str(len(data)))
            return False
    else:
        return False


def get_mac_address(hostname):
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
    mac = get_mac_address(hostname)
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
