#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import subprocess
from elftools.elf.elffile import ELFFile

def extract(elf_name):
    with open(elf_name, 'rb') as f:
        elffile = ELFFile(f)
        text = elffile.get_section_by_name('.text')
        shellcode = text.data()
        return shellcode

def format_shellcode(shellcode):
    return ''.join(map(lambda s:'\\x'+s.encode('hex'), list(shellcode)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[-1]
        objname = '/tmp/'+os.path.basename(filename)+'.o'
        asm = ['as', filename, '-o', objname]
        if '--32' in sys.argv[1:-1]:
            asm.append('--32')
        elif '--64' in sys.argv[1:-1]:
            asm.append('--64')

        proc = subprocess.Popen(asm, stdin=subprocess.PIPE)
        proc.stdin.close()
        proc.wait()
        ret = proc.returncode

        if ret == 0:
            shellcode = extract(objname)
            print format_shellcode(shellcode)
            os.remove(objname)
        else:
            print "ASM Error"
    else:
        print 'Usage: ', sys.argv[0], '[--32|--64] filename'


