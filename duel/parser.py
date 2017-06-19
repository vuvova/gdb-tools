from __future__ import unicode_literals
from arpeggio import ZeroOrMore, Optional, EOF, RegExMatch, Match, Terminal, \
                     ParserPython, PTNodeVisitor, visit_parse_tree, OneOrMore
import re
import gdb
from duel import expr

try: a=unichr # Python 3 compatibility
except: unichr=chr

escapes=r"""\\(?:[abefnrtv"'?]|[0-7]{1,3}|x[0-9a-fA-F]+|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})"""

# typespec parser
types = dict()
def make_typespec_parser():
    self = Match('(cast)')
    def chars(): return RegExMatch(r'[0-9a-zA-Z_*& :,]+')
    def ts(): return OneOrMore([chars,('(',ts,')'),('[',ts,']'),('<',ts,'>')])
    def cast(): return '(',ts,')'
    parser=ParserPython(cast, autokwd=True, debug=False)
    def parse_ts(s):
        try:
            parse_tree=parser.parse(s)
            tstr = s[parse_tree[1].position:parse_tree[2].position]
            if tstr not in types:
                t = gdb.parse_and_eval('('+tstr+' *)0').type.target()
                types[tstr] = t
            return (parser.position, tstr)
        except:
            return (0, None)
    def parse(parser):
        c_pos = parser.position
        (matchlen, t) = parse_ts(parser.input[c_pos:])
        if t:
            matched = parser.input[c_pos:c_pos + matchlen]
            if parser.debug:
                parser.dprint(
                    "++ Match '%s' at %d => '%s'" %
                    (matched, c_pos, parser.context(matchlen)))
            parser.position += matchlen
            return Terminal(self, c_pos, t)
        else:
            if parser.debug:
                parser.dprint("-- NoMatch at {}".format(c_pos))
            parser._nm_raise(self, c_pos, parser)
    self.to_match=self.rule_name
    self._parse = parse
    return self

cast = make_typespec_parser()

def real(): return RegExMatch(r'\d+(([eE][+-]?\d+)|\.\d+([eE][+-]?\d+)?)')
def hexadecimal(): return RegExMatch(r'0[xX][0-9A-Fa-f]*\b')
def decimal(): return RegExMatch(r'[1-9][0-9]*\b')
def octal(): return RegExMatch(r'0[0-7]*\b')
def char(): return RegExMatch(r"'([^'\\]|"+escapes+")'")
def string(): return RegExMatch(r'"([^\\"]|'+escapes+')*"')
def ident(): return RegExMatch(r'[A-Za-z_]\w*')
def underscores(): return RegExMatch(r'_+')
def ident_or_func(): return ident, Optional('(', Optional(expression), ')')
def parens(): return [('(', expression, ')'), ('{', expression, '}')]
def term21(): return [real, hexadecimal, decimal, octal, char, string,
                      underscores, ident_or_func ]
def term20(): return [
            term21,
            parens
        ]
def term19a(): return term20, Optional('#', ident)
def term19(): return term19a, ZeroOrMore([
            (['.', '->', '-->', '@'], term19a),
            ('[', expression, ']'),
            ('[[', expression, ']]'),
        ])
def term18(): return ZeroOrMore(['&&/', '||/', '#/', '-', '*', '&', '!', '~', cast]), term19,
def term17(): return term18, ZeroOrMore(['/', '*', '%'], term18)
def term16(): return term17, ZeroOrMore(['-', '+'], term17)
def term15(): return term16, ZeroOrMore(['<<', '>>'], term16)
def term14(): return [(term15, Optional('..', Optional(term15))), ('..', term15)]
def term13(): return term14, ZeroOrMore(['<=?', '>=?', '<?', '>?','<=', '>=', '<', '>' ], term14)
def term12(): return term13, ZeroOrMore(['==?', '!=?', '==', '!='], term13)
def term11(): return term12, ZeroOrMore(RegExMatch(r'&(?!&)', str_repr='&'), term12)
def term10(): return term11, ZeroOrMore('^', term11)
def term9():  return term10, ZeroOrMore('|', term10)
def term8():  return term9, ZeroOrMore('&&', term9)
def term7():  return term8, ZeroOrMore('||', term8)
def term6():  return term7, Optional('?', term6, ':', term6)
#def term5():  return term6, ZeroOrMore(['=', '+=', '-=', '*=', '/='], term6)
def term4():  return Optional(ident, ':='), term6
def term3():  return term4, ZeroOrMore(',', term4)
def term2():  return term3, ZeroOrMore('=>', term1)
def ifterm(): return 'if', '(', expression , ')', term1, Optional('else', term1)
#def whileterm(): return 'while', '(', expression , ')', term1
#def forterm(): return 'for', '(', term2, ';', term2, ';', term2, ')', term1
def term1():  return [ ifterm, term2 ]
def term0():  return term1, ZeroOrMore(';', term1)
def expression(): return term0,
def input(): return expression, EOF

parser=ParserPython(input, autokwd=True, debug=False)

def type_error(s): raise TypeError(s)
def not_implemented(): raise NotImplementedError("Not implemented yet")

def getchar(s):
    escmap = {'a':'\a', 'b':'\b', 'e':'\033', 'f':'\f', 'n':'\n',
              'r':'\r', 't':'\t', 'v':'\v', '"':'"', "'":"'", '?':'?' }
    if s[0] != '\\': return s[0], s[1:]
    if s[1] in escmap: return escmap[s[1]], s[2:]
    if s[1] == 'u': return unichr(int(s[2:6], 16)), s[6:]
    if s[1] == 'U': return unichr(int(s[2:10], 16)), s[10:]
    if s[1] == 'x':
        m = re.match('([0-9a-fA-F]+)(.*)', s[2:])
        return unichr(int(m.group(1), 16)), m.group(2)
    m = re.match('([0-7]{1,3})(.*)', s[1:])
    return unichr(int(m.group(1), 8)), m.group(2)

class DuelVisitor(PTNodeVisitor):
    def visit__default__(self, node, ch):
        node.suppress=False
        return super(DuelVisitor, self).visit__default__(node, ch)
    def visit_real(self, node, ch):
        return expr.Literal(node.value, gdb.Value(float(node.value)))
    def visit_decimal(self, node, ch):
        return expr.Literal(node.value, gdb.Value(int(node.value, 10)))
    def visit_octal(self, node, ch):
        return expr.Literal(node.value, gdb.Value(int(node.value, 8)))
    def visit_hexadecimal(self, node, ch):
        return expr.Literal(node.value, gdb.Value(int(node.value, 16)))
    def visit_string(self, node, ch):
        s, tail = '', node.value[1:-1]
        while tail:
            head, tail = getchar(tail)
            s += head
        return expr.Literal(node.value, gdb.Value(s))
    def visit_char(self, node, ch):
        c, _ = getchar(node.value[1:-1])
        c = gdb.Value(ord(c)).cast(gdb.lookup_type('char'))
        return expr.Literal(node.value, c)
    def visit_ident(self, node, ch):
        return expr.Ident(node.value)
    def visit_underscores(self, node, ch):
        return expr.Underscore(node.value)
    def visit_ident_or_func(self, node, ch):
        if len(ch) == 1: return ch[0]
        if len(ch) == 3: return expr.Call(ch[0], expr.List([]))
        if isinstance(ch[2], expr.List): return expr.Call(ch[0], ch[2])
        return expr.Call(ch[0], expr.List([ch[2]]))
    def visit_parens(self, node, ch):
        op, arg = ch[0], ch[1]
        if op == '(': return expr.Unary('({})', arg, lambda x: x)
        if op == '{': return expr.Curlies(arg)
    def visit_term19a(self, node, ch):
        if len(ch) == 1: return ch[0]
        return expr.Enumerate(ch[0], ch[2])
    def visit_term19(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '[':   l, _ = expr.Binary(l, '{}[{}]', r, lambda x,y: x[int(y)]), ch.pop(0)
            elif op == '.':   l    = expr.Struct(l, '{}.{}', r)
            elif op == '->':  l    = expr.Struct(l, '{}->{}', r)
            elif op == '-->': l    = expr.StructWalk(l, r)
            elif op == '[[':  l, _ = expr.TakeNth(l, r), ch.pop(0)
            elif op == '@':   l    = expr.Until(l, r)
        return l
    def visit_term18(self, node, ch):
        r = ch.pop()
        while (len(ch)):
            op = ch.pop()
            if   op == '#/':  r = expr.Count(r)
            elif op == '&&/': r = expr.LazyGrouping(op, r, 1, lambda i, x: 1 if i and x else 0)
            elif op == '||/': r = expr.LazyGrouping(op, r, 0, lambda i, x: 1 if i or x else 0)
            elif op == '-':   r = expr.Unary(op, r, lambda x: -x)
            elif op == '*':   r = expr.Unary(op, r, lambda x: x.dereference())
            elif op == '&':   r = expr.Unary(op, r, lambda x: x.address or type_error("Not addressable"))
            elif op == '!':   r = expr.Unary(op, r, lambda x: gdb.Value(not x))
            elif op == '~':   r = expr.Unary(op, r, lambda x: ~x)
            elif op == '++':  not_implemented()
            elif op == '--':  not_implemented()
            else:             r = expr.Unary('('+op+')', r, lambda x: x.cast(types[op]))
        return r
    def visit_term17(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '*': l = expr.Binary(l, op, r, lambda x,y: x*y)
            elif op == '/': l = expr.Binary(l, op, r, lambda x,y: x/y)
            elif op == '%': l = expr.Binary(l, op, r, lambda x,y: x%y)
        return l
    def visit_term16(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '+': l = expr.Binary(l, op, r, lambda x,y: x+y)
            elif op == '-': l = expr.Binary(l, op, r, lambda x,y: x-y)
        return l
    def visit_term15(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '<<': l = expr.Binary(l, op, r, lambda x,y: x<<y)
            elif op == '>>': l = expr.Binary(l, op, r, lambda x,y: x>>y)
        return l
    def visit_term14(self, node, ch):
        if len(ch) == 1: return ch[0]
        if len(ch) == 3: return expr.BiRange(ch[0], ch[2])
        if ch[0] == '..': return expr.URange('..{}', ch[1], True)
        return expr.URange('{}..', ch[0], False)
    def visit_term13(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '<':   l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x<y))
            elif op == '>':   l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x>y))
            elif op == '<=':  l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x<=y))
            elif op == '>=':  l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x>=y))
            elif op == '<?':  l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x<y))
            elif op == '>?':  l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x>y))
            elif op == '<=?': l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x<=y))
            elif op == '>=?': l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x>=y))
        return l
    def visit_term12(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '==':   l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x==y))
            elif op == '!=':   l = expr.Binary(l, op, r, lambda x,y: gdb.Value(x!=y))
            elif op == '==?':  l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x==y))
            elif op == '!=?':  l = expr.Filter(l, op, r, lambda x,y: gdb.Value(x!=y))
        return l
    def visit_term11(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '&': l = expr.Binary(l, op, r, lambda x,y: x&y)
        return l
    def visit_term10(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '^': l = expr.Binary(l, op, r, lambda x,y: x^y)
        return l
    def visit_term9(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '|': l = expr.Binary(l, op, r, lambda x,y: x|y)
        return l
    def visit_term8(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '&&': l = expr.Binary(l, op, r, lambda x,y: 1 if x and y else 0)
        return l
    def visit_term7(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '||': l = expr.Binary(l, op, r, lambda x,y: 1 if x or y else 0)
        return l
    def visit_term6(self, node, ch):
        if len(ch) == 1: return ch[0]
        return expr.Ternary('{} ? {} : {}', ch[0], ch[2], ch[4])
    def visit_term5(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '=':   not_implemented()
            elif op == '+=':  not_implemented()
            elif op == '-=':  not_implemented()
            elif op == '*=':  not_implemented()
            elif op == '/=':  not_implemented()
        return l
    def visit_term4(self, node, ch):
        if len(ch) == 1: return ch[0]
        return expr.Alias(ch[0], ch[2])
    def visit_term3(self, node, ch):
        if len(ch) == 1: return ch[0]
        return expr.List(ch[::2])
    def visit_term2(self, node, ch):
        l = ch.pop(0)
        while len(ch):
            op, r = ch.pop(0), ch.pop(0)
            if   op == '=>': l = expr.Foreach(l, r)
        return l
    def visit_ifterm(self, node, ch):
        if len(ch) == 1: return ch[0]
        if len(ch) == 5: return expr.Ternary('if({}) {}', ch[2], ch[4], None)
        return expr.Ternary('if({}) {} else {}', ch[2], ch[4], ch[6])
    def visit_whileterm(self, node, ch):
        if len(ch) == 1: return ch[0]
        not_implemented()
    def visit_forterm(self, node, ch):
        if len(ch) == 1: return ch[0]
        not_implemented()
    def visit_term0(self, node, ch):
        if len(ch) == 1: return ch[0]
        return expr.Statement(ch[::2])

def eval(arg):
    parse_tree=parser.parse(arg)

    #from arpeggio.export import PTDOTExporter
    #PTDOTExporter().exportFile(tree, "tree.dot")
    #import pprint
    #pprint.PrettyPrinter(indent=4).pprint(parse_tree)

    expr.scopes = list()
    expr.underscores = list()
    expr_tree = visit_parse_tree(parse_tree, DuelVisitor(debug=False))
    assert len(expr.scopes) == 0
    assert len(expr.underscores) == 0

    for name, val in expr_tree.eval():
        gdb.write('{} = {}\n'.format(name, expr.val2str(val)))
