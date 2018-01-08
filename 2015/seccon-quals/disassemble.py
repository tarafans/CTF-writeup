#!/usr/bin/python
import requests
import struct
import socket
import telnetlib
import pwnlib
import pwn
def readuntil(f, delim='\n'):
    data = ''
    while not data.endswith(delim):
        data += f.read(1)
    return data
def p(v):
    return struct.pack('<I', v)
def u(v):
    return struct.unpack('<I', v)[0]
def dis(hex_val):
    url = 'http://www2.onlinedisassembler.com/odaweb/_set'
    cookies = {'sessionid':'2h4isq6ytst6gu9rqu9wn9ryngrotk50',
           '_ga':'GA1.2.722795681.1417831855',
           '_gat': '1'}
    payload = {'arch':'z80',
        'base_address':'',
        'hex_val':hex_val,
        'endian':'default'}
    r = requests.post(url, data=payload, cookies=cookies)
    url = 'http://www2.onlinedisassembler.com/odaweb/_refresh'
    payload = {'id': '19884'}
    r = requests.post(url, data=payload, cookies=cookies)
    result = r.text
    import re
    pat = re.compile("<insn>(.*)</insn>")
    return pat.findall(result)[0]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('disassemble.quals.seccon.jp', 23168))
f = s.makefile('rw', bufsize=0)
i = 0
while(True):
    print 'round: %d' % i
    ret = readuntil(f, ': ')
    assem = readuntil(f, '\n').replace(' ','').replace('\n','')
    readuntil(f, '? ')
    print assem
    result = dis(assem)
    print result
    f.write(result + '\n')
    i += 1
    if (i == 100): break
print f.read(1024)
