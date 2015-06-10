import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.0.5',7777))
s.send(str.encode('data'))
result = s.recv(4092)
result.decode()
print(result)

