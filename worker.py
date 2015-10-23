import server
import hypervisor
import socket
import json
import threading
import time
import storage


cloud = []
cloud_lock = threading.Lock()
print_lock = threading.Lock()
pingTime = 5


# TODO: resources, sync resources based on their settings in .cloud.json


def run():
    '''run server, listen on port'''
    global cloud
    global cloud_lock
    global print_lock
    with cloud_lock:
        localhost = server.get_server_props()
        localhost['lastPing'] = time.time()
        cloud.append(localhost)
        cloud += server.scan_cloud()

    host = server.get_hostname()
    port = server.get_cloud_port()
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
    data = ''
    while True:
        # TODO: incomplete data error
        conn, addr = s.accept()

        # ERROR this is blocking: data = conn.recv(5120, socket.MSG_WAITALL)

        '''
        ERROR: this blocks
        data = ""
        part = None
        while part != "":
            part = conn.recv(4096)
            part = part.decode()
            data += part
        '''

        ''' DEZE BLOKKEERT
        data = ""
        tmp = conn.recv(20 * 1024)
        print('receiving...')
        while tmp:
            print('receiving in loop ...')
            data += tmp.decode()
            tmp = conn.recv(20 * 1024)
        print('receive done...')
        '''

        ''' DEZE GEEFT INCOMPLEET '''
        tmp = conn.recv(20 * 1024)
        data = tmp.decode()
        cmd = data.split()
        if (cmd):
            result = do_command(cmd)
            conn.sendall(str(result).encode())
        conn.close()

        ''' DEZE WERKT OOK NIET tmp = conn.recv(20 * 1024) data += tmp.decode()
        print('socket data: ' + str(addr))
        # print('=============================')
        # print(data)
        if '\n' in data:
            # print('new line found')
            cmd = data.split()
            if (cmd):
                result = do_command(cmd)
                result += '\n'
                conn.sendall(str(result).encode())
            data = ''
        conn.close()
        print('closed')
        '''



def migrate(guest_name, to_server):
    # TODO: check if resource is mounted on <to_server>
    guests = get_guest_list()
    localhost_name = server.get_hostname()
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
            return 'migrate job started'
        else:
            # Send migrate job to guest's host
            cmd = 'cmd {"action":"migrate","guest":"' + guest_name
            cmd += '","to_server":"' + to_server + '"}'
            ip = socket.gethostbyname(guest['host'])
            print('Sending migrate command to: ' + guest['host'])
            return server.get_from_socket(command=cmd, ip=ip)
    else:
        return 'Guest ' + guest_name + ' not found'


def migrate_all(from_server, to_server):
    ''' migrate all guests from one host to another '''
    localhost_name = server.get_hostname()
    if from_server == localhost_name:
        guests = get_guest_list()
        for guest in guests:
            if guest['host'] == localhost_name:
                return migrate(guest['name'], to_server)
    else:
        # Send migrate job to guest's host
        cmd = 'cmd {"action":"migrateAll","from_server":"' + from_server
        cmd += '","to_server":"' + to_server + '"}'
        ip = socket.gethostbyname(from_server)
        print('Sending migrateAll command to: ' + from_server)
        return server.get_from_socket(command=cmd, ip=ip)


def create_share(path):
    ''' create share on server'''
    localhost_name = server.get_hostname()
    server_name = localhost_name
    p = path.split(':')
    if len(p) == 2:
        server_name = p[0]
        path = p[1]
    if server_name == localhost_name:
        # create share on local server
        return storage.create_share(path)
    else:
        # send create share to server <server_name>
        cmd = 'cmd {"action":"create_share","path":"' + path + '"}'
        ip = socket.gethostbyname(server_name)
        return server.get_from_socket(command=cmd, ip=ip)


def mount(share_name, server_name):
    ''' mount <shareName> on server <serverName>'''
    print('mounting ' + share_name + ' on ' + server_name)
    localhost_name = server.get_hostname()
    if server_name == localhost_name:
        share = False
        for s in get_share_list():
            if s['server'] + ':' + s['path'] == share_name:
                share = s
                break
        if share is not False:
            return storage.mount(share)
        else:
            return 'Share ' + share_name + ' not found'
    else:
        # Send mount job to guest's host
        cmd = 'cmd {"action":"mount","share_name":"' + share_name
        cmd += '","server_name":"' + server_name + '"}'
        ip = socket.gethostbyname(server_name)
        print('Sending mount command to: ' + server_name)
        return server.get_from_socket(command=cmd, ip=ip)


def do_command(cmd):
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
            cloud_add_server(s)
        except:
            print('received invalid json: ' + data + '\nlength: ' + str(len(data)))
        props = server.get_server_props()
        props = json.dumps(props)
        return props
    elif cmd[0] == 'guests':
        guests = get_guest_list()
        guests = json.dumps(guests)
        return guests
    elif cmd[0] == 'shares':
        shares = get_share_list()
        shares = json.dumps(shares)
        return shares
    elif cmd[0] == 'mounts':
        mounts = get_mount_list()
        mounts = json.dumps(mounts)
        return mounts
    elif cmd[0] == 'resources':
        resources = get_resources()
        resources = json.dumps(resources)
        return resources
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
            return migrate_all(cmd['from_server'], cmd['to_server'])
        elif cmd['action'] == 'mount':
            return mount(cmd['share_name'], cmd['server_name'])
        elif cmd['action'] == 'create_share':
            return create_share(cmd['path'])

        return 'invalid action: ' + str(cmd['action'])


def get_ips_to_scan():
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
    localIp = server.get_server_ip(server.get_hostname())
    while True:
        ips = get_ips_to_scan()
        for ip in ips:
            if not ip == localIp:  # handshake to remote server
                srv = server.handshake(ip)
                if srv:
                    cloud_add_server(srv)
                else:
                    cloud_remove_server(ip)
            else:  # update localhost
                srv = server.get_server_props()
                cloud_add_server(srv)
        time.sleep(pingTime)


def threaded_migrate(guest, to_server):
    hypervisor.guest_migrate(guest, to_server)


def cloud_has_server(srv):
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


def cloud_add_server(srv):
    '''add a server to the cloud'''
    global cloud
    global cloud_lock
    srv['lastPing'] = time.time()
    if not cloud_has_server(srv):  # add server to cloud
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


def cloud_remove_server(ip):
    global cloud
    global cloud_lock
    with cloud_lock:
        # print('cloud locked remove server')
        for s in range(len(cloud)):
            if cloud[s]['ip'] == ip:
                del cloud[s]
                break
    # print('cloud unlocked remove server')


def get_guest_list():
    '''return list of all vm's in the cloud'''
    global cloud
    global cloud_lock
    vmlist = []
    with cloud_lock:
        for s in cloud:
            vmlist = vmlist + s['guests']
    return vmlist


def get_share_list():
    '''return list of all nfs shares in the cloud'''
    global cloud
    global cloud_lock
    shares = []
    with cloud_lock:
        for s in cloud:
            shares = shares + s['shares']
    return shares


def get_mount_list():
    '''return list of all nfs shares in the cloud'''
    global cloud
    global cloud_lock
    mounts = []
    with cloud_lock:
        for s in cloud:
            mounts = mounts + s['mounts']
    return mounts


def get_resources():
    '''get list of resources'''
    global cloud
    global cloud_lock
    res = {
        'guests': {},
        'shares': {}
    }
    with cloud_lock:
        for srv in cloud:
            print(srv['name'])
            for g in srv['guests']:
                if g['name'] in res['guests']:
                    pass
                else:
                    res['guests'][g['name']] = {
                        'image_path': g['image_path'],
                        'running': True,
                        'shares': []}
            for s in srv['shares']:
                if 'meta' in s:
                    if s['meta']['type'] == 'guest':
                        if s['meta']['guest_name'] in res['guests']:
                            pass
                        else:
                            image_path = '/mnt/' + srv['name'] + '/' + s['name'] + '/' + s['meta']['guest_name'] + '.img'
                            res['guests'][s['meta']['guest_name']] = {
                                'image_path': image_path,
                                'running': False,
                                'shares': []}
                        res['guests'][s['meta']['guest_name']]['shares'].append(s)
    return res
