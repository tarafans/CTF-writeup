set $i = 1474081200 
b *0x080494ca
b *0x8049829

command 1
set $eax=$i
set $i = $i - 1
p/d $i
c
end

command 2
if strcmp($eax, "otpauth://totp/1000717357?secret=CU62GUZJQPIQJH5KFJBFP5QE54XN5O6DLGVXGORQ5L7QFFSKHTHQ") == 0
	p/d $i - 1
	x/s $eax
	x/8wx 0x81a9800
	q
end

set $eax=0x1
set $ecx=0x0
set $edx=0x81a6204
set $ebx=0x6
set $esp=0xffffd5d0
set $ebp=0xffffd5f8
set $esi=0xffffd6a4
set $edi=0xffffd80d
set $eip=0x80492cd
set $eflags=0x246
set *0xffffd5dd=0x06010001
set *0xffffd5d4=1000717357
c
end

set pagination off
r -g -k 1000717357 -o 1000717357
