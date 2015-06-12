import socket
import time

def portscan(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.01)
        s.connect((ip, port))
        s.close()
        return True
    except:
        s.close()
        return False

def findSSHservers():
    gevonden = 0
    for x in range(0,256):
        ip = "10.0.0." + str(x)
        # print "scanning: " + ip
        if portscan(ip, 22):
            print 'Port 22 is open op ip:' + ip
            gevonden += 1
    print str(gevonden) + " ssh servers gevonden"

start = time.time()
findSSHservers()
end = time.time()
print "in " + str(end - start) + " seconden"
