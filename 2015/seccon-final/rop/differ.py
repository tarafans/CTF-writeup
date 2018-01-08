import struct
import string

f1 = open('v1.log', 'r')
f2 = open('v2.log', 'r')
f3 = open('v3.log', 'r')
f4 = open('v4.log', 'r')

c1 = f1.readlines()
c2 = f2.read()
c3 = f3.read()
c4 = f4.read()

for i in xrange(len(c1)):
	addr = c1[i].split(':')
	if len(addr)>=2 and addr[0] in c2 and addr[0] in c3 and addr[0] in c4:
		print addr[0]
