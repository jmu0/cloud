import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.0.5',7777))
s.send(str.encode('data'))
data = ""
while True:
    buf =  s.recv(1024)
    data += buf
    if not buf or buf.find('\n'): break
data = data.decode()
print(data)
