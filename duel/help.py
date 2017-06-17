import re

HEADER = 'DUEL.py 0.9.3, high level data exploration language. "dl" for help\n'

INTRO = """\
Supported DUEL commands:
duel help      - give basic help (shortcut: dl ?)
duel longhelp  - give a longer help (dl ??)
duel examples  - show useful usage examples
duel operators - operators summary
duel aliases   - show current aliases
duel clear     - clear all aliases
"""

with open(__file__.rstrip("pyc") + "md") as f: LONGHELP = ''.join(f)

HELP = """\
Duel - Debugging U (might) Even Like -- A high level data exploration language

Duel was designed to overcome problems with traditional debuggers' print
statement. It supports the C operators, many C constructs, and many new
operators for easy exploration of the program's space, e.g.
x[..100] >? 0                 show positive x[i] for i=0 to 99
y[10..20].code !=? 0          show non-zero y[i].code for i=10 to 20
h-->next->code                expand linked list h->next, h->next->next ...
head-->next.if(code>0) name   show name for each element with code>0
x[i:=..100]=y[i];             array copy. i is an alias to vals 0..99
head-->next[[10..15]]         the 10th to 15th element of a linked list
#/(head-->next->val==?4)      count elements with val==4
head-->next->if(next) val >? next->val    check if list is sorted by val

Duel was created by Michael Golan at Princeton University.
Duel.py is a pure-python Duel implementation by Sergei Golubchik.

Try "dl operators" or "dl longhelp"
"""

OPERATORS = re.sub(r'^(?s).*\nOperators\n---------\n\n*(.*?\n)[^\n]+\n-----+\n.*$', r'\1', LONGHELP)
EXAMPLES = re.sub(r'^(?s).*\nExamples\n--------\n\n*(.*?\n)[^\n]+\n-----+\n.*$', r'\1', LONGHELP)
EXAMPLES = re.sub(r'\n\n', r'\n', EXAMPLES)
