.global exit
exit:
mov 0x4(%esp), %ebx
mov $0x1, %eax
int $0x80
ret

.global write
write:
mov 0x4(%esp), %ebx
mov 0x8(%esp), %ecx
mov 0xc(%esp), %edx
mov $0x4, %eax
int $0x80
ret

.global open
open:
mov 0x4(%esp), %ebx
mov 0x8(%esp), %ecx
mov 0xc(%esp), %edx
mov $0x5, %eax
int $0x80
ret

.global execve
execve:
mov 0x4(%esp), %ebx
mov 0x8(%esp), %ecx
mov 0xc(%esp), %edx
mov $0xb, %eax
int $0x80
ret

.global setuid
setuid:
mov 0x4(%esp), %ebx
mov $0x17, %eax
int $0x80
ret

.global ioctl
ioctl:
mov 0x4(%esp), %ebx
mov 0x8(%esp), %ecx
mov 0xc(%esp), %edx
mov $0x36, %eax
int $0x80
ret
