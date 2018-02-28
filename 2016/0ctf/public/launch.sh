#!/bin/sh

stty intr ^]

qemu-system-i386 -m 64M -kernel ./bzImage -initrd ./initramfs.cpio.gz -nographic -append "root=/dev/ram rw console=ttyS0 rdinit=/sbin/init oops=panic panic=1 quiet" -monitor /dev/null -cpu qemu64,+smap,+smep 2>/dev/null
