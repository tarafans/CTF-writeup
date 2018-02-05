flag = ''

b7 = [70, 108, 97, 103, 123, 83, 48, 109, 101, 48, 102, 85, 53]
for c in b7:
  flag += chr(c)
flag += '#'

b9 = [103, 110, 105, 107, 48, 48, 76, 51, 114, 52]
for c in b9[::-1]:
  flag += chr(c)
flag += '#'

b2 = '1234567890'
b3 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
b4 = 'abcdefghijklmnopqrstuvwxyz'

bb = b3[0]
bb += b4[19]
bb += b3[19]
bb += b4[7]
bb += b2[2]
bb += b3[18]
bb += b4[19]
bb += b2[3]
bb += b4[17]
bb += b4[18]

flag += bb

print flag
