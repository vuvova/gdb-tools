#!/usr/bin/python

from subprocess import Popen, PIPE
from os import execlp
from os.path import dirname
import re

stem=__file__.rstrip('py')
with open(stem+'gdb', 'r') as fg, open(stem+'in', 'w') as fi, open(stem+'out', 'w') as fo:
    for l in fg:
        if l.startswith('(gdb) '):
            fi.write(l[6:])
        else:
            fo.write(l)
p=Popen(['gdb', '-batch', '-n', '-x', 'test.in'], cwd=dirname(stem), stdout=PIPE, stderr=PIPE, universal_newlines=True)
(o,e)=p.communicate()
if e: raise Exception(e)
o = re.sub(r'(=.*) 0x[0-9a-f]+', r'\1 0xXXXXX', o)
o = re.sub(r'Temporary breakpoint 1 at .*\n', '', o)
o = re.sub(r'\n.*/lib.*\n', '\n', o)
with open(stem+'reject', 'w') as f: f.write(o)
execlp('diff', 'diff', '-us', stem+'out', stem+'reject')
