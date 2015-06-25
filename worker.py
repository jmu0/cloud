import server
import hypervisor
import socket
import json
import threading
import time

cloud = []
cloud_lock = threading.Lock()
print_lock = threading.Lock()
pingTime = 5


def run():
    '''run server, listen on port'''
    global cloud
    global cloud_lock
    global print_lock
    with cloud_lock:
        localhost = server.getServerProps()
        localhost['lastPing'] = time.time()
        cloud.append(localhost)
        cloud += server.scanCloud()

    host = server.getHostName()
    port = server.getCloudPort()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except socket.error as e:
        with print_lock:
            print(str(e))
    s.listen(256)
    with print_lock:
        print('Listening on  port ' + str(port))
    t_scanner = threading.Thread(target=threaded_scanner)
    t_scanner.daemon = True
    t_scanner.start()
    while True:
        conn, addr = s.accept()
        # with print_lock:
        # print('connection from: ' + addr[0] + ":" + str(addr[1]))
        # data = conn.recv(5120, socket.MSG_WAITALL)
        data = conn.recv(10 * 1024)
        data = data.decode()
        # print('received command: ' + str(data))
        cmd = data.split()
        if (cmd):
            result = doCommand(cmd)
            # print('-----result-----')
            # print(result)
            # print('-----end result-----')
            # print('length: ' + str(len(result)))
            conn.sendall(str(result).encode())
        conn.close()


def migrate(guest_name, to_server):
    guests = getGuestList()
    localhost_name = server.getHostName()
    guest = False
    for g in guests:
        if g['name'] == guest_name:
            guest = g
            break
    if guest:
        if guest['host'] == localhost_name:
            # Migrate
            print('start migrate thread')
            args = [guest_name, to_server]
            t_migrate = threading.Thread(target=threaded_migrate, args=args)
            t_migrate.daemon = True
            t_migrate.start()
        else:
            # Send migrate job to guest's host
            cmd = 'cmd {"action":"migrate","guest":"' + guest_name
            cmd += '","to_server":"' + to_server + '"}'
            ip = socket.gethostbyname(guest['host'])
            print('Sending migrate command to: ' + guest['host'])
            server.getFromSocket(command=cmd, ip=ip)
    else:
        return 'Guest ' + guest_name + ' not found'


def migrateAll(from_server, to_server):
    ''' migrate all guests from one host to another '''
    localhost_name = server.getHostName()
    if from_server == localhost_name:
        guests = getGuestList()
        for guest in guests:
            if guest['host'] == localhost_name:
                migrate(guest['name'], to_server)
    else:
        # Send migrate job to guest's host
        cmd = 'cmd {"action":"migrateAll","from_server":"' + from_server
        cmd += '","to_server":"' + to_server + '"}'
        ip = socket.gethostbyname(from_server)
        print('Sending migrateAll command to: ' + from_server)
        server.getFromSocket(command=cmd, ip=ip)


def doCommand(cmd):
    '''do command received from socket connection'''
    global cloud_lock
    global print_lock
    if cmd[0] == 'servers':
        with cloud_lock:
            servers = json.dumps(cloud)
        return servers
    elif cmd[0] == 'handshake':
        ''' receive handshake '''
        data = ''.join(cmd[1:])
        try:
            s = json.loads(data)
            cloudAddServer(s)
        except:
            print('invalid json: ' + data + '\nlength: ' + str(len(data)))
        props = server.getServerProps()
        props = json.dumps(props)
        return props
    elif cmd[0] == 'guests':
        guests = getGuestList()
        guests = json.dumps(guests)
        return guests
    elif cmd[0] == 'shares':
        shares = getShareList()
        shares = json.dumps(shares)
        return shares
    elif cmd[0] == 'mounts':
        mounts = getMountList()
        mounts = json.dumps(mounts)
        return mounts
    elif cmd[0] == 'cmd':
        try:
            cmd = ''.join(cmd[1:])
            cmd = json.loads(cmd)
        except:
            s = 'invalid json: '
            s += str(cmd[1] + '\nlength: ' + str(len(cmd[1])))
            return s
        if cmd['action'] == 'migrate':
            return migrate(cmd['guest'], cmd['to_server'])
        elif cmd['action'] == 'migrateAll':
            return migrateAll(cmd['from_server'], cmd['to_server'])
        elif cmd['action'] == 'mount':
            # TODO: mount command
            pass
        return 'invalid action: ' + str(cmd['action'])


def getIPsToScan():
    global cloud_lock
    ips = []
    t = time.time()
    with cloud_lock:
        # print('cloud locked get ips')
        for s in cloud:
            if t - s['lastPing'] > pingTime:
                ips.append(s['ip'])
    # print('cloud unlocked get ips')
    return ips


def threaded_scanner():
    '''thread to scan and update cloud'''
    localIp = server.getServerIP(server.getHostName())
    while True:
        ips = getIPsToScan()
        for ip in ips:
            if not ip == localIp:  # handshake to remote server
                srv = server.handshake(ip)
                if srv:
                    cloudAddServer(srv)
                else:
                    cloudRemoveServer(ip)
            else:  # update localhost
                srv = server.getServerProps()
                cloudAddServer(srv)
        time.sleep(pingTime)


def threaded_migrate(guest, to_server):
    hypervisor.guest_migrate(guest, to_server)


def cloudHasServer(srv):
    '''return boolean if server exists in the cloud'''
    global cloud
    global cloud_lock
    global print_lock
    with cloud_lock:
        # print('cloud locked hasServer')
        for s in cloud:
            try:
                if s['ip'] == srv['ip']:
                    return True
            except:
                with print_lock:
                    print(s)
                    print(srv)
    # print('cloud unlocked hasServer')
    return False


def cloudAddServer(srv):
    '''add a server to the cloud'''
    global cloud
    global cloud_lock
    srv['lastPing'] = time.time()
    if not cloudHasServer(srv):  # add server to cloud
        with cloud_lock:
            # print('cloud locked add Server')
            cloud.append(srv)
        # print('cloud unlocked add Server')
    else:  # replace existing server
        with cloud_lock:
            # print('cloud locked update Server')
            for i in range(len(cloud)):
                if cloud[i]['ip'] == srv['ip']:
                    cloud[i] = srv
        # print('cloud unlocked update Server')


def cloudRemoveServer(ip):
    global cloud
    global cloud_lock
    with cloud_lock:
        # print('cloud locked remove server')
        for s in range(len(cloud)):
            if cloud[s]['ip'] == ip:
                del cloud[s]
                break
    # print('cloud unlocked remove server')


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
