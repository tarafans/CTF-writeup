## 0ctf 2015 Final

0ctf 2015 Final on April 25 & 26 had ended last week. And finally 217,
Blue-Lotus and FlappyPig won the 1st, 2nd and 3rd place. The final includes 5
attack-defense problems and 2 jeopardy problems.

The 5 attack-defense ones include 1 web pentesting problem and other 3 binary
pwnable and also a code game.

The 2 jeopardy problems include a web pentesting problem and also a Android
pwning one.

Here give a brief writeup of problem lib2, which was not solved by any team
during the game.

The binary is written in C++, and it is a library management platform. Mainly,
it has two types of vulnerability.

One is a use-after-free on the book object. Actually after communicating with
many players after the game, they said that they all realize this vulnerability
but do not have enough time to finish the exploit. Seems this time too many
problems corresponding to such short game time maybe. :P

You can fully controlled the content of the freed book object with anything you
want. And then by that adjusting price function, you can turn this UAF vuln
into a INC [addr] one. You can then do a heap spray(cauz it is a 32bit elf and
heap spray is effective) and inc the highest byte of the name length property,
then read out the book name to get a info leak. That can help you bypass ASLR
and PIE.

And then you can inc the address of the book object stored in an array, and
make the first dword in your book object to be a pointer of the book name
buffer, then the vftable is also fully controlled by you. Since ASLR and PIE
are already bypassed, PWNED ;)

Another type of vuln appears several times in the binary, which integer
overflow when doing multiplication, and then the program will malloc a smaller
area which can lead to a heap overflow. This one can be easier to pwn.

You can download the binary here:
https://www.dropbox.com/s/hqaohr5ewqgj3wn/lib2?dl=0

0ctf event ends this year. Next year we plan to invite more foreign teams like
dcua this year to Shanghai and take part in the 0ctf final event. See you guys
next year ;)

memeda@0ops
