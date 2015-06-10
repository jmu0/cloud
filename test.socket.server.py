import socket
import sys
# import threading


host = '10.0.0.5'
port = 7777 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try: 
    s.bind((host, port))
except socket.error as e:
    print(str(e))
s.listen(5)

# lock = threading.Lock()

def threaded_client(conn):
    conn.send(str.encode('Welcome, type your info \n'))

    while True: 
        data = conn.recv(2046)
        # with lock:
        print "Received: " + data.decode()
        reply = "Server output: " + data.decode()
        if not data:
            # with lock:
            print('Disconnected')
            break
        conn.sendall(str(reply).encode())
    conn.close()


while True:
    conn, addr = s.accept()
    print('connected to: ' + addr[0] + ":" + str(addr[1]))
    data = conn.recv(4092)
    cmd = data.decode().split()
    print(cmd)
    if cmd[0] == 'data':
        conn.sendall(str.encode('hier is de data\n'))
    conn.close()


