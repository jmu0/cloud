import server
import scanner
import socket
import json
import threading
import time

cloud = []
cloud_lock = threading.Lock()


def run():
    '''run server, listen on port'''
    global cloud
    global cloud_lock
    with cloud_lock:
        localhost = server.getServerProps()
        localhost['lastPing'] = time.time()
        cloud.append(localhost)
        cloud += scanner.scanCloud()

    host = server.getHostName()
    port = scanner.getCloudPort()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(256)
    print('Listening on  port ' + str(port))
    t_scanner = threading.Thread(target=threaded_scanner)
    t_scanner.daemon = True
    t_scanner.start()
    while True:
        conn, addr = s.accept()
        print('connection from: ' + addr[0] + ":" + str(addr[1]))
        # data = conn.recv(5120, socket.MSG_WAITALL)
        data = conn.recv(5120)
        data = data.decode()
        cmd = data.split()
        if (cmd):
            result = doCommand(cmd)
            print('-----result-----')
            print(result)
            print('-----end result-----')
            print('length: ' + str(len(result)))
            conn.sendall(str(result).encode())
        conn.close()


def doCommand(cmd):
    '''do command received from socket connection'''
    global cloud_lock
    '''do command from port'''
    if cmd[0] == 'servers':
        with cloud_lock:
            servers = json.dumps(cloud)
        return servers
    if cmd[0] == 'handshake':
        data = ''.join(cmd[1:])
        s = json.loads(data)
        cloudAddServer(s)
        print('handshake from :' + s['ip'])
        props = server.getServerProps()
        props = json.dumps(props)
        return props
    if cmd[0] == 'guests':
        guests = getGuestList()
        guests = json.dumps(guests)
        return guests
    if cmd[0] == 'shares':
        shares = getShareList()
        shares = json.dumps(shares)
        return shares
    if cmd[0] == 'mounts':
        mounts = getMountList()
        mounts = json.dumps(mounts)
        return mounts


def threaded_scanner():
    '''thread to scan and update cloud'''
    global cloud
    global cloud_lock
    pingTime = 5
    localIp = server.getServerIP(server.getHostName())
    while True:
        # print('threaded scan')
        deleteIP = []
        with cloud_lock:
            for s in range(len(cloud)):
                print(cloud[s])
                print(localIp)
                if not cloud[s]['ip'] == localIp:
                    # print('check '+cloud[s]['name'])
                    if time.time() - cloud[s]['lastPing'] > pingTime:
                        ip = cloud[s]['ip']
                        cloud[s] = scanner.handshake(cloud[s]['ip'])
                        if not cloud[s]:
                            deleteIP.append(ip)
                    # else: print('not scanning '+cloud[s]['name'])
            for ip in deleteIP:
                for s in range(len(cloud)):
                    if not cloud[s]:
                        del cloud[s]
                        break
        # print('end threaded scan \n')
        time.sleep(pingTime)


def cloudHasServer(srv):
    '''return boolean if server exists in the cloud'''
    global cloud
    with cloud_lock:
        for s in cloud:
            try:
                if s['ip'] == srv['ip']:
                    return True
            except:
                print(s)
                print(srv)
    return False


def cloudAddServer(srv):
    '''add a server to the cloud'''
    global cloud
    global cloud_lock
    srv['lastPing'] = time.time()
    if not cloudHasServer(srv):  # add server to cloud
        with cloud_lock:
            cloud.append(srv)
    else:  # replace existing server
        with cloud_lock:
            for i in range(len(cloud)):
                if cloud[i]['ip'] == srv['ip']:
                    cloud[i] = srv


def getGuestList():
    '''return list of all vm's in the cloud'''
    global cloud
    global cloud_lock
    vmlist = []
    with cloud_lock:
        for s in cloud:
            vmlist = vmlist + s['guests']
    return vmlist


def getShareList():
    '''return list of all nfs shares in the cloud'''
    global cloud
    global cloud_lock
    shares = []
    with cloud_lock:
        for s in cloud:
            shares = shares + s['shares']
    return shares


def getMountList():
    '''return list of all nfs shares in the cloud'''
    global cloud
    global cloud_lock
    mounts = []
    with cloud_lock:
        for s in cloud:
            mounts = mounts + s['mounts']
    return mounts
