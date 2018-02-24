# gdb-tools

This repository contains various tools used to make the time spent in gdb more
comfortable.

To install these tools, first install the modules with

    pip install gdb-tools

or with `easy_install` or `python setup.py install [--user]`.

Then you need to import corresponding modules into your gdb. Add, for example,

    py import duel

into your `~/.gdbinit`. If you plan to use `pretty_printer` module, I'd
recommend to put all your python gdb enhancements in `~/.gdb.py` and source it
from `~/.gdbinit`.

## pretty_printer.py

A convenience helper to write **gdb pretty-printers**. Import this module and
write new pretty printers as easy as
```python
from pretty_printer import PrettyPrinter

@PrettyPrinter
def st_bitmap(val):
    s=''
    for i in range((val['n_bits']+31)//32):
        s = format(int(val['bitmap'][i]), '032b') + s
    return "b'" + s[-int(val['n_bits']):] + "'"
```
Here `val` is a `gdb.Value` object to print, and `st_bitmap` is the type to
pretty-print (alternatively, a type can be passed to the decorator as an
argument, useful for types that aren't valid Python identifiers). If the type
has a name, either typedef'ed name or the underlying actual type can be used in
the pretty printer definition (useful, for types like
`typedef int set_of_flags`). Pointers are resolved automatically:
```
(gdb) p map
$1 = b'001010111'
(gdb) p &map
$1 = (st_bitmap *) 0x7fff8610 b'001010111'
```

Import this module into your `~/.gdb.py` and create your own pretty printers
there.

## DUEL — Debugging U (might) Even Like

A high level language for exploring various data structures. Created by
Michael Golan in 1993, who implemented it for gdb 4.x. "Insanely cool",
according to gdb developers. This is **DUEL.py** — a pure python implementation
that uses gdb Python API and the [Arpeggio](https://github.com/igordejanovic/Arpeggio)
parser. Install arpeggio (or copy it into `duel/` — it's only 20K) and
`import duel` into your `~/.gdb.py`. Few examples of what DUEL can do:

Command | Explanation
------------ | -------------
`dl ?` | short help
`dl x[10..20,22,24,40..60]` | display `x[i]` for the selected indexes
`dl x[9..0]` | display `x[i]` backwards
`dl x[..100] >? 5 <? 10` | display `x[i]` if `5<x[i]<10`
`dl val[..50].(is_dx ? x : y)` | `val[i].x` or `val[i].y` depending on `val[i].is_dx`
`dl x[i:=..100] >? x[i+1]` | check whether `x[i]` is sorted
`dl (x[..100] >? 0)[[2]]` | return the 3rd positive `x[i]`
`dl argv[0..]@0` | `argv[0]`, `argv[1]`, etc until first null
`dl emp[0..]@(code==0)` | `emp[0]`, `emp[1]`, etc until `emp[n].code==0`
`dl head-->next->val` | `val` of each element in a linked list
`dl head-->(left,right)->val` | `val` of each element in a binary tree
`dl head-->next[[20]]` | element 20 of list
`dl #/head-->next` | count elements on a linked list
`dl #/(head-->next-val>?5)` | count those over 5
`dl head-->(next!=?head)` | expand cyclic linked list

Or read the [manual](duel/help.md).
