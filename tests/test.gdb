(gdb) shell gcc test.c -O0 -ggdb3
(gdb) file a.out
(gdb) py sys.path.append('..')
(gdb) py import duel
Loaded DUEL.py 0.9.6, high level data exploration language
(gdb) help duel
Evaluate Duel expressions.

Duel is a high level data exploration language.
Type "dl" for help
(gdb) dl
Supported DUEL commands:
duel help      - give basic help (shortcut: dl ?)
duel longhelp  - give a longer help (dl ??)
duel examples  - show useful usage examples
duel operators - operators summary
duel aliases   - show current aliases
duel clear     - clear all aliases
(gdb) dl ?
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
(gdb) dl 1
1 = 1
(gdb) dl 2.0
2.0 = 2
(gdb) dl 2e1
2e1 = 20
(gdb) dl 1
1 = 1
(gdb) dl 2.0
2.0 = 2
(gdb) dl 2e1
2e1 = 20
(gdb) dl 2.0e1
2.0e1 = 20
(gdb) dl 020
020 = 16
(gdb) dl 0x20
0x20 = 32
(gdb) dl 019
Expected 'if' or ident or '&&/' or '||/' or '#/' or '+/' or '-' or '*' or '&' or '!' or '~' or '(cast)' or real or hexadecimal or decimal or octal or char or string or underscores or ident or gdbvar or '(' or '{' or '..' at position (1, 1) => '*019'.
(gdb) dl foo
foo = 1
(gdb) dl bar
bar = 2
(gdb) dl s
s = 0xXXXXX "s1"
(gdb) dl 'a'
'a' = 97 'a'
(gdb) dl '\r'
'\r' = 13 '\r'
(gdb) dl '\x20'
'\x20' = 32 ' '
(gdb) dl "foo\7bar"
"foo\7bar" = "foo\abar"
(gdb) dl "\a\r\n\v\t"[2..3]
"\a\r\n\v\t"[2] = 10 '\n'
"\a\r\n\v\t"[3] = 11 '\v'
(gdb) dl "reverse"[6..2]
"reverse"[6] = 101 'e'
"reverse"[5] = 115 's'
"reverse"[4] = 114 'r'
"reverse"[3] = 101 'e'
"reverse"[2] = 118 'v'
(gdb) dl unknown_var
No symbol "unknown_var" in current context.
(gdb) dl (2.0)
2.0 = 2
(gdb) dl {2.0}
2 = 2
(gdb) dl {(2.0)}
2 = 2
(gdb) dl (foo)
foo = 1
(gdb) dl {foo}
1 = 1
(gdb) dl 5[1]
Cannot subscript requested type.
(gdb) dl s[1]
s[1] = 49 '1'
(gdb) dl arr[1]
arr[1] = 10
(gdb) dl arr[foo]
arr[foo] = 10
(gdb) dl arr[{foo}]
arr[1] = 10
(gdb) dl st.i
st.i = 123
(gdb) dl st.(r)
st.r = 3.1415000000000002
(gdb) dl st.{r}
st.3.1415000000000002 = 3.1415000000000002
(gdb) dl tree->v
tree->v = 14
(gdb) dl tree->u
No symbol "u" in current context.
(gdb) dl tree.val
No symbol "val" in current context.
(gdb) dl tree->left->v
tree->left->v = 12
(gdb) dl tree-->left->v
tree->v = 14
tree->left->v = 12
tree-->left[[2]]->v = 8
tree-->left[[3]]->v = 0
(gdb) dl tree-->left->v[[1]]
tree-->left->v[[1]] = 12
(gdb) dl tree-->left->v[[2]]
tree-->left->v[[2]] = 8
(gdb) dl (*tree).v
(*tree).v = 14
(gdb) dl *tree.v
Attempt to take contents of a non-pointer value.
(gdb) dl *1
Attempt to take contents of a non-pointer value.
(gdb) dl *&foo
*&foo = 1
(gdb) dl #/foo
#/foo = 1
(gdb) dl #/{foo}
#/(foo) = 1
(gdb) dl #/tree-->left
#/tree-->left = 4
(gdb) dl #/arr[..2]
#/arr[..2] = 2
(gdb) dl #/(arr[..2] <? 7)
#/(arr[..2] <? 7) = 1
(gdb) dl +/(arr[..2] <? 7)
+/(arr[..2] <? 7) = 5
(gdb) dl &&/foo
&&/foo = 1
(gdb) dl &&/tree-->left->v
&&/tree-->left->v = 0
(gdb) dl ||/arr[..2]
||/arr[..2] = 1
(gdb) dl &&/arr[0..]
&&/arr[0..] = 0
(gdb) dl -5
-5 = -5
(gdb) dl --10
--10 = 10
(gdb) dl -foo
-foo = -1
(gdb) dl !0
!0 = 1
(gdb) dl !foo
!foo = 0
(gdb) dl !{foo}
!1 = 0
(gdb) dl foo + 1
foo + 1 = 2
(gdb) dl ~5
~5 = -6
(gdb) dl ~ 0xFF77
~0xFF77 = -65400
(gdb) dl 10 * 3.14
10 * 3.14 = 31.400000000000002
(gdb) dl arr[foo] / {st.r}
arr[foo] / 3.1415000000000002 = 3.1831927423205473
(gdb) dl st.i % 10
st.i % 10 = 3
(gdb) dl 1 + 2
1 + 2 = 3
(gdb) dl 100 - 9*8
100 - 9 * 8 = 28
(gdb) dl 1 << 8/2
1 << 8 / 2 = 16
(gdb) dl 1024 >> 2*3
1024 >> 2 * 3 = 16
(gdb) dl foo ^ 0x0BEC
foo ^ 0x0BEC = 3053
(gdb) dl 1234 | 0xBABE
1234 | 0xBABE = 48894
(gdb) dl 0xDEAD & 0xBEEF
0xDEAD & 0xBEEF = 40621
(gdb) dl 0xDEAD && 0xBEEF
0xDEAD && 0xBEEF = 1
(gdb) dl foo && 0
foo && 0 = 0
(gdb) dl foo || 0
foo || 0 = 1
(gdb) dl tree->left->left->left->v || 0
tree->left->left->left->v || 0 = 0
(gdb) dl tree-->right->v @ (v <= 11)
tree->v = 14
tree->right->v = 13
(gdb) dl tree-->right @ (v <= 11, 0)
tree = 0xXXXXX <te>
tree->right = 0xXXXXX <td>
tree-->right[[2]] = 0xXXXXX <tb>
(gdb) dl 1..5
1 = 1
2 = 2
3 = 3
4 = 4
5 = 5
(gdb) dl 'x'..'z'
120 'x' = 120 'x'
121 'y' = 121 'y'
122 'z' = 122 'z'
(gdb) dl ..3
0 = 0
1 = 1
2 = 2
(gdb) dl foo..4
1 = 1
2 = 2
3 = 3
4 = 4
(gdb) dl #/(..15)
#/(..15) = 15
(gdb) dl #/1..5
1 = 1
2 = 2
3 = 3
4 = 4
5 = 5
(gdb) dl (..3) + (10..11)
0 + 10 = 10
0 + 11 = 11
1 + 10 = 11
1 + 11 = 12
2 + 10 = 12
2 + 11 = 13
(gdb) dl arr[..2]
arr[0] = 5
arr[1] = 10
(gdb) dl arr[0..]@0
arr[0] = 5
arr[1] = 10
arr[2] = 15
arr[3] = 20
(gdb) dl #/arr[0..]@0
#/arr[0..]@0 = 4
(gdb) dl 1..(2..3)
1 = 1
2 = 2
1 = 1
2 = 2
3 = 3
(gdb) dl 2 < 5
2 < 5 = 1
(gdb) dl foo > arr[foo]
foo > arr[foo] = 0
(gdb) dl 1 >= 2
1 >= 2 = 0
(gdb) dl foo == 10
foo == 10 = 0
(gdb) dl st.i != 20
st.i != 20 = 1
(gdb) dl 1 ? 2 : 3
1 ? 2 : 3 = 2
(gdb) dl foo ? 2 ? 3 : 4 : 5
foo ? 2 ? 3 : 4 : 5 = 3
(gdb) dl !foo ? foo : 2 ? 3 : 4
!foo ? foo : 2 ? 3 : 4 = 3
(gdb) dl ..10 >? 4
5 >? 4 = 5
6 >? 4 = 6
7 >? 4 = 7
8 >? 4 = 8
9 >? 4 = 9
(gdb) dl arr[..2] <=? 6
arr[0] <=? 6 = 5
(gdb) dl ((3..6) * (1..3)) %3 ==? 2
(4 * 2) % 3 ==? 2 = 2
(5 * 1) % 3 ==? 2 = 2
(gdb) dl arr[..2] !=? 5
arr[1] !=? 5 = 10
(gdb) dl 1 >? 0
1 >? 0 = 1
(gdb) dl 1 >? 2
(gdb) dl (i:=5)+9
i + 9 = 14
(gdb) dl arr[i:=..2]
arr[i] = 5
arr[i] = 10
(gdb) dl arr[i:=..2] + i
arr[i] + i = 5
arr[i] + i = 11
(gdb) dl arr[i:=..2] + {i}
arr[i] + 0 = 5
arr[i] + 1 = 11
(gdb) dl x:= "string"
x = "string"
(gdb) dl y:=&foo, *y
y = 0xXXXXX <foo>
*y = 1
(gdb) dl z:=foo
z = 1
(gdb) dl &z
&z = 0xXXXXX <foo>
(gdb) dl &i
Not addressable
(gdb) dl aliases
Aliases table:
i: 1 = 1
x: "string" = "string"
y: &foo = 0xXXXXX <foo>
z: foo = 1
(gdb) dl clear
Aliases table cleared
(gdb) dl aliases
Aliases table empty
(gdb) dl 1..3 => _+5
1 + 5 = 6
2 + 5 = 7
3 + 5 = 8
(gdb) dl ..2 => arr[_]
arr[0] = 5
arr[1] = 10
(gdb) dl 1..3 => .._ => __ + _
1 + 0 = 1
2 + 0 = 2
2 + 1 = 3
3 + 0 = 3
3 + 1 = 4
3 + 2 = 5
(gdb) dl 1,2,3
1 = 1
2 = 2
3 = 3
(gdb) dl #/(1,4,8,16)
#/(1,4,8,16) = 4
(gdb) dl +/(1,4,8,16)
+/(1,4,8,16) = 29
(gdb) dl arr[0,1]
arr[0] = 5
arr[1] = 10
(gdb) dl 1..3,2..4,3..5
1 = 1
2 = 2
3 = 3
2 = 2
3 = 3
4 = 4
3 = 3
4 = 4
5 = 5
(gdb) dl st.(i,r)
st.i = 123
st.r = 3.1415000000000002
(gdb) dl tree-->(left,right)->v
tree->v = 14
tree->left->v = 12
tree-->left[[2]]->v = 8
tree-->left[[3]]->v = 0
tree-->left[[2]]->right->v = 1
tree->left->right->v = 9
tree->left->right->left->v = 2
tree->left-->right[[2]]->v = 3
tree->right->v = 13
tree->right->left->v = 10
tree->right-->left[[2]]->v = 4
tree->right->left->right->v = 5
tree-->right[[2]]->v = 11
tree-->right[[2]]->left->v = 6
tree-->right[[3]]->v = 7
(gdb) dl (100..)#i@(i > 10)
100 = 100
101 = 101
102 = 102
103 = 103
104 = 104
105 = 105
106 = 106
107 = 107
108 = 108
109 = 109
110 = 110
(gdb) dl tree-->left->(if(v>10)v else v+100)
tree->(if(v > 10) v else v + 100) = 14
tree->left->(if(v > 10) v else v + 100) = 12
tree-->left[[2]]->(if(v > 10) v else v + 100) = 108
tree-->left[[3]]->(if(v > 10) v else v + 100) = 100
(gdb) dl #/(100..)#i@(i > 10)
#/(100..)#i@(i > 10) = 11
(gdb) dl tree-->right->(if(v%2)v*v)
tree->right->(if(v % 2) v * v) = 169
tree-->right[[2]]->(if(v % 2) v * v) = 121
tree-->right[[3]]->(if(v % 2) v * v) = 49
(gdb) dl (100..=>if(&&/(2,3..(_-1)=>__%_ )) _)[[..5]]
(100.. => if(&&/(2,3..(_ - 1) => __ % _)) _)[[0]] = 101
(100.. => if(&&/(2,3..(_ - 1) => __ % _)) _)[[1]] = 103
(100.. => if(&&/(2,3..(_ - 1) => __ % _)) _)[[2]] = 107
(100.. => if(&&/(2,3..(_ - 1) => __ % _)) _)[[3]] = 109
(100.. => if(&&/(2,3..(_ - 1) => __ % _)) _)[[4]] = 113
(gdb) dl (int)3.5, (int)3.5 * 10
(int)3.5 = 3
(int)3.5 * 10 = 30
(gdb) dl 1..2;3;x:=4;5;6;x+7
x + 7 = 11
(gdb) dl #/(1..4;x:=5;x+6)
#/(1..4; x := 5; x + 6) = 1
(gdb) start

Temporary breakpoint 1, main () at test.c:15
15	  return 0;
(gdb) dl strncmp("foo", "bar", 1..3)
strncmp("foo","bar",1) = 4
strncmp("foo","bar",2) = 4
strncmp("foo","bar",3) = 4
(gdb) dl (strcmp, strcasecmp)("FOO", "foo")
strcmp("FOO","foo") = -32
strcasecmp("FOO","foo") = 0
(gdb) dl (((1.5))+(((2))))
(1.5 + 2) = 3.5
(gdb) dl ("f-o-o")[((1..3))]
"f-o-o"[1] = 45 '-'
"f-o-o"[2] = 111 'o'
"f-o-o"[3] = 45 '-'
(gdb) dl (1,2+3)*10
1 * 10 = 10
(2 + 3) * 10 = 50
(gdb) set $a=5
(gdb) p $a
$1 = 5
(gdb) dl $a + $1
$a + $1 = 10
(gdb) dl *(char *)s
*(char *)s = 115 's'
