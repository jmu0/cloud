import server
import scanner
import socket
import sys
import pickle


def run():
    cloud = []
    cloud.append(server.getServerProps())

    host = server.getHostName() 
    port = scanner.getCloudPort()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: 
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(256)
    while True:
        conn, addr = s.accept()
        print('connected to: ' + addr[0] + ":" + str(addr[1]))
        data = ""
        while True:
            buf =  conn.recv(1024)
            data += buf
            if not buf or buf.find('\n'): break
        data = data.decode()
        cmd = data.split()
        if (cmd): 
            result = doCommand(cmd)
            conn.sendall(str(result).encode())
        conn.close()

def doCommand(cmd):
    try:
        if cmd[0] == 'sys':
            props = server.getServerProps()
            props = pickle.dumps(props)
            return props
    except:
        pass

