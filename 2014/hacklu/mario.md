## Mario HackLU CTF 2014 Exploiting 500

Recently, I have some spare time so I come back to this problem which our team
didn't solve during the competition. There are no public writeups about this
problem but two public exploits, one from ricky[at]PPP and one from the author
TheJH. It is really a fascinating problem so let's just begin our journey.

### Background

There is a server runnning there and it provides two services, one is
profile\_viewer and the other is a sorter. The service are execl() by the server
process and the client connect to these two servers by unix domain socket.

The source is given.

### Vulnerability

In profile\_viewer.c, there is an arbitrary file-read vulnerability.

```C
FILE *open_profile(FILE *in) {
  char path[256];
  strcpy(path, "user_profiles/");

  // read the username and append it to the path
  if (!fgets(path+14, 512, in)) {
    return NULL;
  }
  if (path[strlen(path)-1] == '\n') {
    path[strlen(path)-1] = '\0';
  }

  return fopen(path, "r");
}
```

Append ../../../../../../.. or something like that to the path, and then we can
get out off the user\_profiles directory.

In sorter.c, there is a main vulnerability which causes code execution. Let's
see.

```C
if ((r=pthread_create(&thread_id, &attrs, handle_con, (void*)(intptr_t)socket))) {
      errno = r;
      perror("pthread_create failed");
      exit(1);
    }
```

Every time there is a service launching request from the user, then it will
create a thread to deal with it.

```C
// read [4 bytes: n], [n bytes: data]
// returns 0 for "end", 1 for "process more data"
int recv_packet(int s, uint32_t l, char *b, uint32_t done) {
/* read length. one byte at a time – easier to handle partial reads that way. */
  if (b == NULL && (l&0x80000000)) {
    uint8_t next_len_char;
    int r = read(s, &next_len_char, 1);
    if (r<0 && errno == EAGAIN) return recv_packet(s, l, b, done);
    if (r<=0) return 0;
    return recv_packet(s, (l<<8)|next_len_char, b, done);
  }

  if (b == NULL) {
    b = malloc(l);
  }
  if (b == NULL) perror("unable to allocate memory"), exit(1);

  if (l == done) {
    int r = handle_packet(s, b, l);
    free(b);
    return r;
  }

  int r = read(s, b+done, l-done);
  if ((r<0 && errno != EAGAIN) || r==0) return 0;
  return recv_packet(s, l, b, done+r);
}

void *handle_con(void *s_) {
  int s = (int)(intptr_t)s_;
  while (recv_packet(s, 0xffffffff, NULL, 0));
  close(s);
  return NULL;
}
```

When the thread is created, recv\_packet is called. It first use a while() loop
to get the length of the data. Notice that here the length is presented in
big-endian.

Once l is not a positive integer, it will try to read the next byte by doing
recursion, otherwise it will then begin to read the data which is stored into
the malloc()'d area, until l bytes are already read. Then it called
handle\_packet.

What the function handle\_packet do is actually not very important, but notice
that it has a large stack frame size, 16064 bytes.

Let's take a look at the memory map of the process sorter.

```text
00400000-00402000 r-xp 00000000 fc:00 1845386                            /home/mario/sorter
00601000-00602000 rw-p 00001000 fc:00 1845386                            /home/mario/sorter
00b4a000-00b6b000 rw-p 00000000 00:00 0                                  [heap]
7fb9a07ae000-7fb9a07af000 ---p 00000000 00:00 0
7fb9a07af000-7fb9a0faf000 rw-p 00000000 00:00 0                          [stack:12724]
7fb9a0faf000-7fb9a0fb0000 ---p 00000000 00:00 0
7fb9a0fb0000-7fb9a17b0000 rw-p 00000000 00:00 0                          [stack:12723]
7fb9a17b0000-7fb9a1932000 r-xp 00000000 fc:00 1849079                    /home/mario/debian-wheezy-libs/libc.so.6
7fb9a1932000-7fb9a1b31000 ---p 00182000 fc:00 1849079                    /home/mario/debian-wheezy-libs/libc.so.6
7fb9a1b31000-7fb9a1b35000 r--p 00181000 fc:00 1849079                    /home/mario/debian-wheezy-libs/libc.so.6
7fb9a1b35000-7fb9a1b36000 rw-p 00185000 fc:00 1849079                    /home/mario/debian-wheezy-libs/libc.so.6
7fb9a1b36000-7fb9a1b3b000 rw-p 00000000 00:00 0
7fb9a1b3b000-7fb9a1b52000 r-xp 00000000 fc:00 1849082                    /home/mario/debian-wheezy-libs/libpthread.so.0
7fb9a1b52000-7fb9a1d51000 ---p 00017000 fc:00 1849082                    /home/mario/debian-wheezy-libs/libpthread.so.0
7fb9a1d51000-7fb9a1d52000 r--p 00016000 fc:00 1849082                    /home/mario/debian-wheezy-libs/libpthread.so.0
7fb9a1d52000-7fb9a1d53000 rw-p 00017000 fc:00 1849082                    /home/mario/debian-wheezy-libs/libpthread.so.0
7fb9a1d53000-7fb9a1d57000 rw-p 00000000 00:00 0
7fb9a1d57000-7fb9a1d77000 r-xp 00000000 fc:00 1849081                    /home/mario/debian-wheezy-libs/ld-2.13.so
7fb9a1f71000-7fb9a1f76000 rw-p 00000000 00:00 0
7fb9a1f76000-7fb9a1f77000 r--p 0001f000 fc:00 1849081                    /home/mario/debian-wheezy-libs/ld-2.13.so
7fb9a1f77000-7fb9a1f78000 rw-p 00020000 fc:00 1849081                    /home/mario/debian-wheezy-libs/ld-2.13.so
7fb9a1f78000-7fb9a1f79000 rw-p 00000000 00:00 0
7fff2300d000-7fff2302e000 rw-p 00000000 00:00 0                          [stack]
7fff23032000-7fff23034000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

You can see there are two stack regions for two threads. There are guard
pages(---p) between the stack regions to make sure that one thread will not
corrupt another. And another important thing is that the mmap() base is just
above the stack area of these two threads, in this map, 0x7fb9a07ae000.

However as I mentioned before, there is a recursive function recv\_packet. If we
feed '\xff' to it during the while() loop, then it'll do recursion times and
times, and also when it begins to read data, it also does recursion. During
that rsp becomes smaller and smaller, and finally be very close to the guard
page.

The vulnerability is that when we get rsp close to the guard page, remind that
large-stack-frame function handle\_packet, if we call it, rsp will minus a very
large number which is definitely larger than the size of the guard page, then
we could jump across the guard page.

And this idea is referenced in The stack is back, Jon Oberheide.

### Exploitation

An very important thing is that we got a file leak, which seems to be a very
powerful weapon. We can read /proc/[pid]/maps to get the memory map of the
thread and also we can read /proc/[pid]/stat to get the exact value of the
thread's stack pointer's location. Oh, btw, we could download the binary of the
link library, which the program uses.

Now we look up into the ways of getting code execution. The vulnerability
causes a memory collision. The main idea is to overwrite the stack of the
thread and get the control of pc. In general there are two ways to exploit it.

In the content below, I use thread 1 to refer the thread whose stack area is at
a higher memory and use thread 2 to refer the thread whose stack area is at a
lower memory.

#### the collision between one thread's stack area and another's stack area

That is ricky's way to exploit it.

We just do hundreds of thousands of recursion to make thread 1's rsp close to
the guard page and then call into handle\_packet.

```C
int handle_packet(int s, char *buf, uint32_t len) {
  // 1000 values should be enough for anyone :D
  struct value values[1000];

  if (len == 0) return 0; // missing input

  // parse input into `values`
  char *p = buf;
  int i = 0; /* index in values; will be member count at the end */
  values[i] = (struct value){.buf = p, .len = 0};
  for (; p<buf+len; p++) {
    if (*p == ',') {
      i++;
      if (i == 1000) return 0; // too much data
      values[i] = (struct value){.buf = p+1, .len = 0};
    } else {
      values[i].len++;
    }
  }
  i++;
  fprintf(stderr, "got %d values\n", i);

  // sort input
  qsort(values, i, sizeof(values[0]), compare_values);

  // assemble response
  char *buf2 = malloc(len);
  p = buf2;
  for (int j = 0; j < i; j++) {
    if (j != 0) *p++ = ',';
    memcpy(p, values[j].buf, values[j].len);
    p += values[j].len;
  }

  // write response
  size_t written = 0;
  ssize_t r;
write_more:
  r = write(s, buf2+written, len-written);
  if (r < 0 && errno == EAGAIN) goto write_more;
  if (r <= 0) {
    free(buf2);
    return 0;
  }
  written += r;
  if (written < len) goto write_more;

  return 1;
}
```

We could see that handle\_packet do a qsort on your input and then write back to
the user. The sorted value is stored in array values.

When we successfully call into handle\_packet in thread 1, we jump across the
guard page between thread1's stack area and thread 2's stack area because of
the large stack frame size of handle\_packet and now rsp is pointing in the
region of thread 2' stack. We could just craft the array values's content and
make it overwrite thread 2' stack's content, like stored return address on the
stack.

The trick is that for thread 1, we could first send all the data except the
last byte, and then recv\_packet will wait there and will not call into
handle\_packet. Then you can read rsp for both threads and do some recursions
for thread 2 to make thread 2' rsp to a proper place. And just send the last
byte, then thread 1 call handle\_packet, overwrite the thread 2's stack. Make
thread 2's current function returns(it is waiting there in read() in the
while() loop), then we finally control pc.

Since it is a stack overwrite, doing ROP is not very hard and the stuff is done.

#### the collision between one thread's stack area and a malloc()'d area

The exploit of the author, TheJH, mainly is based on this.

Now this time we make thread 2's rsp smaller and smaller, finally call into
handle\_packet to jump across the guard page. After sorting, it will write the
result back to the user. So we can make it just hang on at that place, without
reading the result, to make its rsp across the guard page in the mmap() region.

For thread 1, we just malloc() a large space and libc will call mmap() to
satisfy your request and now the collision happens. Just spray your payload in
the mmap()'d area which is also the thread 2's stack area. Overwrite the stack
content of thread2, make thread 2 return, and then we got the control flow.

### At the end

It is really a very nice problem and I learned much. And this problem again
shows a very important security issue,

The virtual memory is limited, but however we could spray the heap to fill up
the memory, we could do recursion to make stack area larger and larger. For any
region in the memory, is it an area of stack, or an area of heap or an area of
mmap() or is it an area of this thread or of another thread? The sad thing is
that at many times, the program is not clear. The only thing it can do is that,
if you want and I have, then OK, no problem, I give you. If you release, then I
am not much concerned about the original use but get back.

memeda@0ops
