import server
import scanner
import socket
import json

cloud = []


def run():
    '''run server, listen on port'''
    global cloud
    cloud.append(server.getServerProps())
    # print(cloud)
    cloud += scanner.scanCloud()
    # print(cloud)

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
    while True:
        conn, addr = s.accept()
        print('connected to: ' + addr[0] + ":" + str(addr[1]))
        data = b''
        while True:
            buf = conn.recv(1024)
            data += buf
            if not buf or str(buf).find('\n'):
                break
        data = data.decode()
        cmd = data.split()
        if (cmd):
            result = doCommand(cmd)
            conn.sendall(str(result).encode())
        conn.close()


def doCommand(cmd):
    '''do command from port'''
    if cmd[0] == 'servers':
        servers = json.dumps(cloud)
        return servers
    if cmd[0] == 'handshake':
        data = ''.join(cmd[1:])
        s = json.loads(data)
        cloudAddServer(s)
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


def cloudHasServer(srv):
    '''return boolean if server exists in the cloud'''
    global cloud
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
    if not cloudHasServer(srv):  # add server to cloud
        cloud.append(srv)
    else:  # replace existing server
        for i in range(len(cloud)):
            if cloud[i]['ip'] == srv['ip']:
                cloud[i] = srv


def getGuestList():
    '''return list of all vm's in the cloud'''
    global cloud
    vmlist = []
    for s in cloud:
        vmlist = vmlist + s['guests']
    return vmlist


def getShareList():
    '''return list of all nfs shares in the cloud'''
    global cloud
    shares = []
    for s in cloud:
        shares = shares + s['shares']
    return shares


def getMountList():
    '''return list of all nfs shares in the cloud'''
    global cloud
    mounts = []
    for s in cloud:
        mounts = mounts + s['mounts']
    return mounts
