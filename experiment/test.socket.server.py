import socket
import sys

#setup socket
host = '10.0.0.5'
port = 7777 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try: 
    s.bind((host, port))
except socket.error as e:
    print(str(e))
s.listen(256)

#command function
def doCommand(cmd):
    print(cmd)
    if cmd[0] == 'data':
        return "hier is de data\n"

#endless loop
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
    conn.sendall(str(doCommand(cmd)).encode())
    conn.close()
