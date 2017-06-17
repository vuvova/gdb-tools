DUEL - A high level data exploration language for gdb
=====================================================

Duel is a special purpose language designed for concise state
exploration of debugged C programs, currently implemented for the GNU
gdb.  Duel is invoked by entering the gdb command `duel` (or `dl`)
instead of `print`:

    (gdb) dl x[1..10] >? 5
    x[3] = 14
    x[8] = 6

prints the array elements `x[1]` to `x[10]` that are greater than 5.
The output includes the values 14 and 6, as well as their symbolic
representation "x[3]" and "x[8]".

Note that some gdb concepts (such as the value history) do not work
with the `dl` command, and Duel expressions are not understood by
other gdb command.

Quick Start
-----------

Duel is based on expressions which return multiple values. The `x..y`
operator returns all integers from `x` to `y`; the `x,y` operator
returns `x` and then `y`, e.g.

    (gdb) dl (1,9,12..15,22)

prints 1, 9, 12, 13, 14, 15 and 22. Such expressions can be used
wherever a single value is used, e.g.

    (gdb) dl x[0..99]

prints first 100 elements of array `x`.

Aliases are defined with `x:=y`:

    (gdb) dl if(x[i:=0..99]<0) x[i]
    x[i] = -4

The symbolic output "x[i]" can be fixed by surrounding `i` with curly
braces, i.e.

    (gdb) dl if(x[i:=0..99]<0) x[{i}]
    x[7] = -4

The curly braces are like parentheses, but they replace the symbolic
representation of the argument with its value. You can usually avoid
this altogether with direct Duel operators:

    (gdb) dl x[..100] <? 0
    x[7] = -4

The `..n` operator is a shorthand for `0..n-1`, that is, "first n
elements of the array". The `x<?y`, `x==?y`, `x>=?y`, etc., operators
compare their left side operand to their right side operand as in C,
but return the left side value if the comparison result is true.
Otherwise, they look for the next values to compare, without returning
anything.

Operators `x.y` and `x->y` allow an expression `y`, evaluated under
`x` scope:

    (gdb) dl emp[..100].(if(code>400) (code,name))
    emp[46].code = 682
    emp[46].name = "Ela"

The `if()` expression is evaluated under the scope of each element of
`emp[]`, an array of structures.

A useful alternative to loops is the `x=>y` operator. It returns `y`
for each value of `x`, setting `_` to reference the value of `x`, e.g.

    (gdb) ..100 => if(emp[_].code>400) emp[_].code,emp[_].name

Using `_` instead of `i` also avoids the need for curly braces.  When `=>`
operators are nested, `__` refers to the parent scope value, `___` to the
great-parent, and so on.

Finally, the `x-->y` operator expands lists and other data structures.
If `head` points to a linked list threaded through the `next` field, then:

    (gdb) dl head-->next->data
    head->data = 12
    head->next->data = 14
    head-->next[[2]]->data = 20
    head-->next[[3]]->data = 26

produce the data field for each node in the list. `x-->y` returns `x`,
`x->y`, `x->y->y`, `x->y->y->y`, etc. until a NULL is found. The
symbolic output "x-->y[[n]]" indicates that `->y` was applied n times.
`x[[y]]` is also the selection operator:

    (gdb) head-->next[[3]]->data
    head-->next[[3]]->data = 26

For example,

    (gdb) dl head-->next[[50..60]]->data

return the 50th through the 60th elements in the list. The `#/x`
operator counts the number of values, so

    (gdb) dl #/( head-->next->data >? 50 )

counts the number of data elements over 50 on the list.

Operator `x@y` stops `x` generating values, as soon as `y` becomes
true.  It is mainly used with the unbounded `x..` range:

    (gdb) dl argv[0..]@(_ == 0)
    argv[0] = 0x7fffffffe2bb "./a.out"
    argv[1] = 0x7fffffffe2dd "--foo"
    argv[2] = 0x7fffffffe300 "--bar"
    argv[3] = 0x7fffffffe306 "42"

The `@(_ == const)` is so common, that it can be abbreviated to
`@const`:

    (gdb) dl argv[0..]@0

Semantics
---------

Duel's semantics are modeled after the Icon programming language. The
input consists of expressions which return sequences of values. C
statements are expressions, too. Typically binary operators evaluate
its operands and produce one result value for every combination of
values from the left and right operands.

For example, in `(5,3)+(6..8)`, the evaluation of `+` first retrieves
the operands 5 and 6, to compute and return 5+6. Then 7, the next
right operand is retrieved and 5+7 is returned, followed by 5+8. Since
there are no other right operand value, the next left operand, 3 is
fetched.  The right operand's computation is restarted returning 6,
and 3+6 is returned. The final return values are 3+7 and 3+8:

    (gdb) dl (5,3)+(6..8)
    (5) + (6) = 11
    (5) + (7) = 12
    (5) + (8) = 13
    (3) + (6) = 9
    (3) + (7) = 10
    (3) + (8) = 11

The computation for operators like `x>?y` is similar, but when the
condition is false, the next values are fetched instead of returning a
value, reducing the sequence of `x` values to those that satisfy the
condition. Operators like `..` return a sequence of values for each
pair of operands.

Duel types also follow the C semantics, with some important
differences. C types are checked statically; Duel types are checked
when operators are applied, e.g., `(1,1.0)/2` returns 0 (int) and 0.5
(double); `(x,y).z` returns `x.z` and `y.z` even if `x` and `y` are of
different types, as long as they both have a field `z`.

Commands
---------

Command        | Description
-------------- | -------------
`duel`         | prints the list of commands
`dl`           | alias for `duel`
`dl help`      | prints short help
`dl ?`         | alias for `dl help`
`dl longhelp`  | prints this help file
`dl ??`        | alias for `dl longhelp`
`dl examples`  | prints **Examples** section of this file
`dl operators` | prints **Operators** section of this file
`dl aliases`   | prints the list of aliases, see `x:=y` operator below
`dl clear`     | clears the list of aliases

Operators
---------

Variables and functions of the program being debugged can be read and
called normally and work as expected.

The complete list of operators, in the precedence order:

* `(x)`, `{x}` - curly braces work as parentheses, but print the value
  of `x`, not its symbolic representation.
* `x#y` - for every value of `x`, set `y` to the index of this `x`
  value (0, 1, ...).
* `x.y`, `x->y`, `x-->y`, `x[y]`, `x[[y]]`, `x@y` - the first two
  operators are *scope* operators, they evaluate `y` in the scope of
  `x`. The third one walks the linked list, evaluating `x`, `x->y`,
  `x->y->y`, etc until NULL. The fourth is a familiar C array element
  access, the fifth takes the `y`-th value in the sequence of values
  of `x`. The last one stops `x` from generating values as soon as `y`
  (evaluated in the scope of `x`) becomes true. If `y` is a literal,
  stops as soon as `x` value becomes equal to `y`. If `y` is a
  sequence of values, stops when at least one value in the sequence is
  true, and prints `x` if at least one value in the sequence is false.
* `(cast)x`, `-x`, `*x`, `&x`, `!x`, `~x`, `#/x`, `&&/x`, `||/x` -
  first six are conventional unary C operators, the last three are
  *grouping* operators.  The first one counts the numbers of values of
  `x`, second returns a boolean AND of all values of `x`, third —
  boolean OR. Just like in C, AND and OR operators are lazy and stop
  as soon as the result value is known.
* `x/y`, `x*y`, `x%y` - conventional C operators.
* `x-y`, `x+y` - conventional C operators.
* `x<<y`, `x>>y` - conventional C operators.
* `x..y`, `..x`, `x..` - ranges. First returns integers from `x` to
  `y`, inclusive (`x` can be greater than `y`, for counting
  backwards). Second returns first `x` integers starting from 0 (in
  other words, it works like `0..x-1`). Last returns an unlimited list
  of integers starting from `x`, and is normally used with `x@y`.
* `x<=y`, `x>=y`, `x<y`, `x>y`, `x<=?y`, `x>=?y`, `x<?y`, `x>?y` -
  first four are conventional C operators, the second four return `x`
  if the condition is true, otherwise they return nothing (so, they
  work like a filter of the `x` value sequence).
* `x==y`, `x!=y`, `x==?y`, `x!=?y` - same. First two are conventional
  C operators, the other two are filters.
* `x&y` - conventional C operator.
* `x^y` - conventional C operator.
* `x|y` - conventional C operator.
* `x&&y` - conventional C operator.
* `x||y` - conventional C operator.
* `x?y:z` - conventional C operator.
* `x:=y` - create an alias `x` for the value of `y`. Note, that it is
  an *alias* to `y`, not a copy of `y` value. If `y` value changes,
  the value of the alias will change too.  Use `dl aliases` and `dl
  clear` commands to see and, respectively, clear the list of aliases.
* `x,y` - creates a sequence of two values.
* `x=>y` - for every value of `x`, store it in `_` and evaluate `y`.
* `if (x) y else z`, `if (x) y` - C statement turned into an operator.
  In the first form it's equivalent to `x?y:z`, in the second form it
  has a filter semantics, returning `y` for every non-zero `x`
  (equivalent to `x !=? 0 => y`).
* `x;y` - evaluate x, ignoring all the results, then evaluate y.

Examples
--------

Compute simple expression:

    dl (0xff-0x12)*3

Display multiplication table:

    dl (1..10)*(1..10)

Display `x[i]` for the selected indexes:

    dl x[10..20,22,24,40..60]

Display `x[i]` backwards:

    dl x[9..0]

Display `x[i]` elements that are greater than 5:

    dl x[..100] >? 5

Display `x[i]` elements that are between 5 and 10:

    dl x[..100] >? 5 <? 10

Same:

    dl x[0..99]=>if(_>5 && _<10) _

Same, if `x[i]` elements are integers:

    dl x[..100] ==? 6..9

Display `y[x[i]]` for each non-zero `x[i]`:

    dl y[x[..100] !=? 0]

Display both `emp[i].code` and `emp[i].name` for first 50 `emp[]` elements

    dl emp[..50].(code,name)

Display `val[i].singl` or `val[i].doubl` depending on `val[i].is_doubl`:

    dl val[..50].(is_doubl?doubl:singl)

Display `hash[i].scope` for non-null `hash[i]`:

    dl (hash[..1024]!=?0)->scope

Check if `x[i]` array is sorted:

    dl x[i:=..100] >? x[i+1]

Check if x has non-unique elements:

    dl x[i:=..100] ==? x[j:=..100] => if(i<j) x[{i,j}]

Same:

    dl if(x[i:=..99] == x[j:=i+1..99]) x[{i,j}]

Find the first positive `x[i]`

    dl (x[..100] >? 0)[[0]]

Find first five positive `x[i]`

    dl (x[..100] >? 0)[[..5]]

Return the first `x[i]` greater than 6 (note, no limit on i):

    dl (x[0..] >? 6)[[0]]

Display `argv[]` array until the first NULL:

    dl argv[0..]@0

Display `emp[]` values until `emp[i].code` is 0:

    dl emp[0..]@(code==0)

Walk the linked list by the `next` pointer, starting from `head`, print `val` of each list element:

    dl head-->next->val

Display the 21st element of a linked list:

    dl head-->next[[20]]

Count elements on a linked list:

    dl #/head-->next

Find the last element in a linked list:

    dl x-->y[[#/x-->y - 1]]

Walk the cyclic linked list (start from `head`, walk until seeing `head` again):

    dl head-->(next!=?head)

Walk the binary tree:

    dl root-->(left,right)->key

Select matching strings from the array:

    dl strncmp(items[i:=0..20], "foo", 3) ==? 0 => items[i]

Find first 10 primes greater than 1000:

    dl (1000..=>if(&&/(2,3.._-1=>__%_ )) _)[[..10]]

To Do
-----

Features of the original Duel, that are not implemented in the
Duel.py yet:

* Builtins: `frame()`, `sizeof()`, `frames_no`, `func.x`
* Variables: `int i; i=5; i++`
* Assignments: `x[..10]=0`
* `while` and `for` operators

Features that were not in the original Duel:
* gdb scope specification: `file.c::var`
* gdb convenience  variables and functions: `$_exitcode`, `$_streq()`, etc


Author
------

Duel was designed by Michael Golan as part of a PhD thesis in the
Computer Science Department of Princeton University. He also
implemented Duel in C as a patch for gdb 4.x.

Duel.py is a pure-python implementation written by Sergei Golubchik

Duel stands for Debugging U (might) Even Like, or Don't Use this
Exotic Language. Judge for yourself!
