
import struct

up32 = lambda x: struct.unpack('<I', x)[0]

f = open('1.txt', 'rb')
s = f.read()

l = 0
i = 0
while i < len(s):
	c = ord(s[i])
	output = ''

	l = i

	if c == 4:
		output = 'dup'
		i += 1
	elif c == 8:
		output = 'not'
		i += 1
	elif c == 48:
		output = 'or'
		i += 1
	elif c == 0x38:
		output = 'pop'
		i += 1
	elif c ==  0x3e:
		output = 'add'
		i += 1
	elif c == 0x3f:
		output = 'call ' + hex((i + ord(s[i+1]) & 0xff))
		i += 2
	elif c == 0x4d:
		output = 'ret'
		i += 1
	elif c == 0x58:
		output = 'push ' + hex(up32(s[i+1:i+5]))
		i += 5
	elif c == 0x72:
		output = 'and'
		i += 1
	elif c == 0x9a:
		output = 'shl'
		i += 1
	elif c == 0xb8:
		output = 'sub'
		i += 1
	elif c == 0xc1:
		output = 'div'
		i += 1
	elif c == 0xc3:
		output = 'if *sp goto ' + hex(i + 2)
		output += ' else goto ' + hex( (ord(s[i + 1]) + i) & 0xff )	
		i += 2
	elif c == 0xca:
		output = 'mul'
		i += 1
	elif c == 0xcf:
		output = 'dup2'
		i += 1
	elif c == 0xe0:
		output = 'shr'
		i += 1
	elif c == 0xe9:
		output = 'get index(' + str(ord(s[i + 1])) + ')'
		i += 2
	elif c == 0xf9:
		output = 'swap'
		i += 1
	elif c == 0xff:
		output = 'xor'
		i += 1
	elif c == 0:
		output = 'end'
		i += 1
	else:
		output = 'nop'		
		i += 1

	print '%s: %s' % (hex(l), output)
	
f.close()
