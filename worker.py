import server
import hypervisor
import scanner
import socket
import json
import threading
import time

cloud = []
cloud_lock = threading.Lock()
print_lock = threading.Lock()


def run():
    '''run server, listen on port'''
    global cloud
    global cloud_lock
    global print_lock
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
        with print_lock:
            print('connection from: ' + addr[0] + ":" + str(addr[1]))
        # data = conn.recv(5120, socket.MSG_WAITALL)
        data = conn.recv(5120)
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


def migrate(cmd):
    # TODO: move to hypervisor module
    guest_name = cmd['guest']
    to_server = cmd['to_server']
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
            cmd = 'cmd ' + json.dumps(cmd)
            ip = socket.gethostbyname(guest['host'])
            print('Sending migrate command to: ' + guest['host'])
            scanner.getFromSocket(command=cmd, ip=ip)
    else:
        return 'Guest ' + guest_name + ' not found'


def doCommand(cmd):
    '''do command received from socket connection'''
    global cloud_lock
    global print_lock
    if cmd[0] == 'servers':
        with cloud_lock:
            servers = json.dumps(cloud)
        return servers
    if cmd[0] == 'handshake':
        ''' receive handshake '''
        data = ''.join(cmd[1:])
        s = json.loads(data)
        cloudAddServer(s)
        # with print_lock:
        #     print('handshake from :' + s['ip'])
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
    if cmd[0] == 'cmd':
        try:
            cmd = ''.join(cmd[1:])
            cmd = json.loads(cmd)
        except:
            return 'invalid json: ' + str(cmd[1])
        if cmd['action'] == 'migrate':
            return migrate(cmd)
        elif cmd['action'] == 'migrateAll':
            pass
        return 'invalid action: ' + str(cmd['action'])


def threaded_scanner():
    '''thread to scan and update cloud'''
    global cloud
    global cloud_lock
    pingTime = 5
    localIp = server.getServerIP(server.getHostName())
    while True:
        deleteIP = []
        with cloud_lock:
            for s in range(len(cloud)):
                if not cloud[s]['ip'] == localIp:
                    # handshake to remote server
                    if time.time() - cloud[s]['lastPing'] > pingTime:
                        ip = cloud[s]['ip']
                        cloud[s] = scanner.handshake(cloud[s]['ip'])
                        if not cloud[s]:
                            deleteIP.append(ip)
                else: 
                    # update localhost
                    if time.time() - cloud[s]['lastPing'] > pingTime:
                        print('scanner updates localhost')
                        cloud[s] = server.getServerProps()
            for ip in deleteIP:
                for s in range(len(cloud)):
                    if not cloud[s]:
                        del cloud[s]
                        break
        # print('end threaded scan \n')
        time.sleep(pingTime)


def threaded_migrate(guest, to_server):
    hypervisor.migrate(guest, to_server)


def cloudHasServer(srv):
    '''return boolean if server exists in the cloud'''
    global cloud
    global cloud_lock
    global print_lock
    with cloud_lock:
        for s in cloud:
            try:
                if s['ip'] == srv['ip']:
                    return True
            except:
                with print_lock:
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
