import server
import scanner
import socket
import json

cloud = []


def run():
    '''listen on port'''
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
    if cmd[0] == 'sys':
        props = server.getServerProps()
        props = json.dumps(props)
        return props
    if cmd[0] == 'handshake':
        data = ''.join(cmd[1:])
        s = json.loads(data)
        cloudAddServer(s)
        props = server.getServerProps()
        props = json.dumps(props)
        return props


def cloudHasServer(srv):
    global cloud
    for s in cloud:
        if s['ip'] == srv['ip']:
            return True
    return False


def cloudAddServer(srv):
    global cloud
    if not cloudHasServer(srv):
        cloud.append(srv)
        print(cloud)
