#include <link.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <wait.h>
#include <sys/mman.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <linux/limits.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "seccomp-bpf.h"

#define MATERIAL_BASEADDR   0x10000000
#define PAYLOAD_MAXLEN      4096
#define KEYWORD_MAXLEN      256
#define TIMEOUT             5
#define ERROR(msg)          fprintf(stderr, "%s(%d): %s\n",\
    __FILE__, __LINE__, msg)
#define SECRET_MAXLEN       256
#define TEAMFLAG_MAX        64
#define RECORD_FNAME        "record.bin"
#define TEAMFLAG_FNAME      "/var/www/teamflag.txt"
#define CHILD_UID           31337
#define CHILD_GID           31337
#define ROPOLYGLOT_UID      1001
#define ROPOLYGLOT_GID      1001

extern char __executable_start[];
extern char _end[];
void get_self(void **paddr, size_t *plen)
{
    *paddr = (void*)__executable_start;
    *plen = (size_t)(_end - __executable_start);
}

int map_executable_section(char *fname, void *baddr)
{
    int         retval = 0;
    FILE        *fp = NULL;
    size_t      nread;
    Elf32_Ehdr  ehdr;
    Elf32_Phdr  phdr;
    uint16_t    phidx;

    fp = fopen(fname, "rb");
    if(fp == NULL){
        ERROR("fopen");
        retval = -1;
        goto END;
    }

    nread = fread(&ehdr, sizeof(ehdr), 1, fp);
    if(nread != 1){
        ERROR("fread");
        retval = -1;
        goto END;
    }

    if(ehdr.e_phoff < sizeof(ehdr)
    || ehdr.e_phentsize != sizeof(phdr)){
        ERROR("invalid binary");
        retval = -1;
        goto END;
    }
    fseek(fp, ehdr.e_phoff - sizeof(ehdr), SEEK_CUR);

    for(phidx = 0; phidx < ehdr.e_phnum; phidx++){
        nread = fread(&phdr, sizeof(phdr), 1, fp);
        if(nread != 1){
            ERROR("fread");
            retval = -1;
            goto END;
        }
        if(phdr.p_type == PT_LOAD && phdr.p_flags & PF_X){
            mmap(baddr + phdr.p_vaddr, phdr.p_memsz, PROT_READ|PROT_EXEC,
                MAP_PRIVATE, fileno(fp), phdr.p_offset);
        }
    }

END:
    if(fp){
        fclose(fp);
    }
    return retval;
}

int restrict_syscalls()
{
    struct sock_filter filter[] = {
        VALIDATE_ARCHITECTURE,
        EXAMINE_SYSCALL,
        ALLOW_SYSCALL(mprotect),
        ALLOW_SYSCALL(open),
        ALLOW_SYSCALL(read),
        ALLOW_SYSCALL(write),
        ALLOW_SYSCALL(close),
        ALLOW_SYSCALL(exit_group),
        ALLOW_SYSCALL(munmap),
        KILL_PROCESS,
    };
    struct sock_fprog fprog = {
        sizeof(filter) / sizeof(filter[0]),
        filter,
    };

    if(prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0){
        ERROR("prctl");
        return -1;
    }

    if(prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &fprog) < 0){
        ERROR("prctl");
        return -1;
    }

    return 0;
}


typedef void (*UNMAP_SELF)(void *ptr, size_t len, char *rop_payload);
__asm__(
"unmap_self:"
    "mov  $0x5b, %eax;"         // munmap
    "mov  4(%esp), %ebx;"       // ptr
    "mov  8(%esp), %ecx;"       // len
    "int  $0x80;"
    "call geteip;"
"geteip:"
    "mov  $0x5b, %eax;"         // munmap
    "pop  %ebx;"                // eip
    "mov  12(%esp), %esp;"      // esp=rop_payload
    "and  $0xfffff000, %ebx;"   // ptr
    "mov  $0x00001000, %ecx;"   // len
    "int  $0x80;"
"sizeof_unmap_self = .-unmap_self;"
    "ret;"
);

extern char unmap_self[];
extern char sizeof_unmap_self[];

void start_rop(char *payload)
{
    int         rslt;
    char        *code_region;
    UNMAP_SELF  entry;
    void        *addr;
    size_t      len;

    get_self(&addr, &len);

    // allocate 2 pages
    code_region = mmap(NULL, getpagesize() * 2, PROT_READ|PROT_WRITE|PROT_EXEC,
        MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    memset(code_region, 0xcc, getpagesize() * 2);

    // copy unmap_self() to the end of the 1st page
    entry = (UNMAP_SELF)(code_region + getpagesize() - (int)sizeof_unmap_self);
    memcpy(entry, (void*)unmap_self,
        (size_t)sizeof_unmap_self + 1/* for ret */);
    mprotect(code_region, getpagesize() * 2, PROT_READ|PROT_EXEC);

    // restrict syscalls
    rslt = restrict_syscalls();
    if(rslt < 0){
        _exit(-1);
    }

    // goto unmap_self 
    entry(addr, len, payload);
}

int recv_data(char *data, size_t maxlen, FILE *fp)
{
    int     len;
    size_t  nread;

    memset(data, 0x00, maxlen);

    // recv the length of data
    nread = fread(&len, sizeof(len), 1, fp);
    if(nread != 1){
        ERROR("fread");
        return -1;
    }
    if(len < 0 || len > maxlen){
        ERROR("invalid length");
        return -1;
    }

    nread = fread(data, 1, len, fp);
    if(nread != len){
        ERROR("fread");
        return -1;
    }

    return len;
}

char *rootdirs[] = {
    "arch00",
    "arch01",
    "arch02",
    "arch03",
};

pid_t child_pid = 0;
void timeout(int sig)
{
    if(child_pid > 0) kill(child_pid, SIGKILL);
    exit(-1);
}

int init_child(char *rootdir)
{
    if(chroot(rootdir) < 0)
        return -1;
    if(chdir("/") < 0)
        return -1;
    if(setgid(CHILD_GID) < 0)
        return -1;
    if(setuid(CHILD_UID) < 0)
        return -1;

    return 0;
}

void update_record_if_needed(int success_cnt, int payload_len,
char *teamflag, int teamflag_len)
{
    struct record{
        int        nsuccess;
        int        npayload;
    } best;
    FILE    *record_fp = NULL;
    FILE    *flag_fp = NULL;
    int     update_flag = 0;
    int     nread;

    record_fp = fopen(RECORD_FNAME, "r+");
    if(record_fp == NULL){
        ERROR("fopen");
        goto END;
    }
    flock(fileno(record_fp), LOCK_EX);

    nread = fread(&best, sizeof(best), 1, record_fp);
    if(nread != 1){
        best.nsuccess = 1;
        best.npayload = PAYLOAD_MAXLEN;
    }
    if(best.nsuccess < success_cnt
    || (best.nsuccess == success_cnt && best.npayload >= payload_len)){
        update_flag = 1;
    }

    if(update_flag){
        best.nsuccess = success_cnt;
        best.npayload = payload_len;
        rewind(record_fp);
        fwrite(&best, sizeof(best), 1, record_fp);
        flag_fp = fopen(TEAMFLAG_FNAME, "wb");
        if(flag_fp == NULL){
            ERROR("fopen");
            goto END;
        }
        fwrite(teamflag, 1, teamflag_len, flag_fp);
        printf("New record: %d,%d\n", success_cnt, payload_len);
    }else{
        printf("Best record: %d,%d\n", best.nsuccess, best.npayload);
    }

END:
    if(flag_fp){
        fclose(flag_fp);
    }
    if(record_fp){
        flock(fileno(record_fp), LOCK_UN);
        fclose(record_fp);
    }

    return;
}

void print_keywords(unsigned int keyword_set)
{
    FILE    *keyword_fp;
    char    keyword[KEYWORD_MAXLEN];
    int     cnt;

    keyword_fp = fopen("keywords.txt", "r");
    if(keyword_fp == NULL){
        ERROR("fopen");
        goto END;
    }
    for(cnt = 0; cnt < sizeof(rootdirs) / sizeof(rootdirs[0]); cnt++){
        fgets(keyword, sizeof(keyword), keyword_fp);
        if(keyword_set & (1<<cnt)){
            printf("%s", keyword);
        }
    }

END:
    if(keyword_fp){
        fclose(keyword_fp);
    }

    return;
}

void report(int success_cnt)
{
    int                 rslt;
    struct sockaddr_in  addr;
    socklen_t           addr_len = sizeof(addr);
    char                cmd[256];

    rslt = getpeername(0, (struct sockaddr*)&addr, &addr_len);
    if(rslt < 0){
        ERROR("getpeername");
        return;
    }
    snprintf(cmd, sizeof(cmd), "./report.py %s %d %d 1> /dev/null 2>&1 &",
        inet_ntoa(addr.sin_addr),
        success_cnt?1:0,
        (int)time(NULL));

    system(cmd);

    return;
}


int main(int argc, char *argv[])
{
    char    payload[PAYLOAD_MAXLEN];
    int     payload_len;
    int     pipefd[2];
    int     cnt;
    int     rslt;
    char    answer[SECRET_MAXLEN];
    char    secret[SECRET_MAXLEN];
    FILE    *secret_fp = NULL;
    char    secret_fname[PATH_MAX];
    int     success_cnt;
    FILE    *fp_out;
    char    teamflag[TEAMFLAG_MAX];
    int     teamflag_len;
    unsigned int keyword_set = 0;

    if(argc < 2){
        ERROR("invalid parameter");
        goto END;
    }
    chdir(argv[1]);

    // set signal handler for SIGALRM
    if(signal(SIGALRM, timeout) == SIG_ERR){
        ERROR("signal");
        goto END;
    }
    alarm(TIMEOUT);

    // recv defense keyword
    rslt = recv_data(teamflag, sizeof(teamflag), stdin);
    if(rslt < 0){
        ERROR("recv_teamflag failed");
        goto END;
    }
    teamflag_len = rslt;

    // recv rop payload
    rslt = recv_data(payload, sizeof(payload), stdin);
    if(rslt < 0){
        ERROR("recv_payload failed");
        goto END;
    }
    payload_len = rslt;

    // create procs for polyglot
    success_cnt = 0;
    memset(answer, 0x00, sizeof(answer));
    memset(secret, 0x00, sizeof(secret));
    for(cnt = 0; cnt < sizeof(rootdirs)/ sizeof(char*); cnt++){
        // prepare pipe
        rslt = pipe(pipefd);
        if(rslt < 0){
            ERROR("pipe");
            goto END;
        }

        // fork
        child_pid = fork();
        if(child_pid < 0){
            ERROR("fork");
            goto END;
        }

        if(child_pid == 0){    // child
            // chroot, setuid, ...
            rslt = init_child(rootdirs[cnt]);
            if(rslt < 0){
                //ERROR("init_child");
                _exit(-1);
            }

            // init stdin, stdout, stderr
            close(pipefd[0]);
            close(0);
            dup2(pipefd[1], 1);
            close(pipefd[1]);
            close(2);

            // map material to MATERIAL_BASEADDR
            rslt = map_executable_section("material", (void*)MATERIAL_BASEADDR);
            if(rslt < 0){
                //ERROR("map_executable_section failed");
                _exit(-1);
            }

            // start rop
            start_rop(payload);
            // never return

        }else{            // parent
            // init pipe
            close(pipefd[1]);
            fp_out = fdopen(pipefd[0], "rb");
            if(fp_out == NULL){
                ERROR("fdopen");
                goto END;
            }

            // read "secret"
            snprintf(secret_fname, sizeof(secret_fname), "%s/secret",
                rootdirs[cnt]);
            secret_fp = fopen(secret_fname, "rb");
            if(secret_fp == NULL){
                ERROR("fopen");
                goto END;
            }
            fread(secret, 1, sizeof(secret), secret_fp);
            fclose(secret_fp);
            secret_fp = NULL;

            // recv answer, and then check it
            fread(answer, 1, sizeof(answer), fp_out);
            if(memcmp(secret, answer, sizeof(answer)) == 0){
                success_cnt++;
                keyword_set |= 1<<cnt;
            }
            fclose(fp_out);
            fp_out = NULL;

            memset(answer, 0x00, sizeof(answer));
            memset(secret, 0x00, sizeof(secret));
            waitpid(child_pid, NULL, 0);
            child_pid = 0;
        }
    }
    alarm(0);

    // update record and flag page if needed
    update_record_if_needed(success_cnt, payload_len, teamflag, teamflag_len);

    // print attack keywords
    print_keywords(keyword_set);

    setgid(ROPOLYGLOT_GID);
    setuid(ROPOLYGLOT_UID);
    report(success_cnt);

END:
    if(child_pid > 0){
        kill(child_pid, SIGKILL);
    }

    return 0;
}
