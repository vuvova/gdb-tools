#!/usr/bin/gdb -x

shell gcc test.c -O0 -ggdb3
file a.out
py sys.path.append('.')
py import duel
set height 0
dl ?
dl 1
dl 2.0
dl 2e1
dl 1
dl 2.0
dl 2e1
dl 2.0e1
dl 020
dl 0x20
dl 019
dl foo
dl bar
dl s
dl 'a'
dl '\r'
dl '\x20'
dl "foo\7bar"
dl "\a\r\n\v\t"[2..3]
dl "reverse"[6..2]
dl unknown_var
dl (2.0)
dl {2.0}
dl {(2.0)}
dl (foo)
dl {foo}
dl 5[1]
dl s[1]
dl arr[1]
dl arr[foo]
dl arr[{foo}]
dl st.i
dl st.(r)
dl st.{r}
dl tree->v
dl tree->u
dl tree.val
dl tree->left->v
dl tree-->left->v
dl tree-->left->v[[1]]
dl tree-->left->v[[2]]
dl (*tree).v
dl *tree.v
dl *1
dl *&foo
dl #/foo
dl #/{foo}
dl #/tree-->left
dl #/arr[..2]
dl #/(arr[..2] <? 7)
dl &&/foo
dl &&/tree-->left->v
dl ||/arr[..2]
dl &&/arr[0..]
dl -5
dl --10
dl -foo
dl !0
dl !foo
dl !{foo}
dl foo + 1
dl ~5
dl ~ 0xFF77
dl 10 * 3.14
dl arr[foo] / {st.r}
dl st.i % 10
dl 1 + 2
dl 100 - 9*8
dl 1 << 8/2
dl 1024 >> 2*3
dl foo ^ 0x0BEC
dl 1234 | 0xBABE
dl 0xDEAD & 0xBEEF
dl 0xDEAD && 0xBEEF
dl foo && 0
dl foo || 0
dl tree->left->left->left->v || 0
dl tree-->right->v @ (v <= 11)
dl tree-->right @ (v <= 11, 0)
dl 1..5
dl 'x'..'z'
dl ..3
dl foo..4
dl #/(..15)
dl #/1..5
dl (..3) + (10..11)
dl arr[..2]
dl arr[0..]@0
dl #/arr[0..]@0
dl 1..(2..3)
dl 2 < 5
dl foo > arr[foo]
dl 1 >= 2
dl foo == 10
dl st.i != 20
dl 1 ? 2 : 3
dl foo ? 2 ? 3 : 4 : 5
dl !foo ? foo : 2 ? 3 : 4
dl ..10 >? 4
dl arr[..2] <=? 6
dl ((3..6) * (1..3)) %3 ==? 2
dl arr[..2] !=? 5
dl 1 >? 0
dl 1 >? 2
dl (i:=5)+9
dl arr[i:=..2]
dl arr[i:=..2] + i
dl arr[i:=..2] + {i}
dl x:= "string"
dl y:=&foo, *y
dl z:=foo
dl &z
dl &i
dl aliases
dl clear
dl aliases
dl 1..3 => _+5
dl ..2 => arr[_]
dl 1..3 => .._ => __ + _
dl 1,2,3
dl #/(1,4,8,16)
dl arr[0,1]
dl 1..3,2..4,3..5
dl st.(i,r)
dl tree-->(left,right)->v
dl (100..)#i@(i > 10)
dl tree-->left->(if(v>10)v else v+100)
dl #/(100..)#i@(i > 10)
dl tree-->right->(if(v%2)v*v)
dl (100..=>if(&&/(2,3..(_-1)=>__%_ )) _)[[..5]]
dl (int)3.5, (int)3.5 * 10
start
dl strncmp("foo", "bar", 1..3)
c
quit
