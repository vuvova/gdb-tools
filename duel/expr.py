import gdb
import sys

try: a=xrange # Python 3 compatibility
except: xrange=range

aliases = dict()
scopes = list()
underscores = list()

def scoped(f):
    def wrapped_eval(self):
        try:
            for x in f(self): yield x
        except GeneratorExit:
            scopes.pop()
            underscores.pop()
    return wrapped_eval

def underscored(f):
    def wrapped_eval(self):
        try:
            for x in f(self): yield x
        except GeneratorExit:
            underscores.pop()
    return wrapped_eval

def val2str(v):
    try: v = v.referenced_value() if v.type.code==gdb.TYPE_CODE_REF else v
    except: pass
    return str(v)

class Expr(object):
    def name(self): return self.name_
    def value(self): return self.value_
    def eval(self): yield self.name(), self.value()

class Literal(Expr):
    def __init__(self, n, v): self.name_, self.value_ = n, v

class Ident(Expr):
    def __init__(self, n): self.name_, self.scope, self.sym = n, None, None
    def symval(self, s): return s.value(gdb.selected_frame()) if s.needs_frame else s.value()
    def value(self):
        if self.scope: return scopes[self.scope][self.name_]
        if self.sym: return self.symval(self.sym)
        if self.name_ in aliases: return aliases[self.name_][1]
        for self.scope in range(len(scopes)-1,-1,-1):
            try: return scopes[self.scope][self.name_]
            except gdb.error: self.scope = None
        try: self.sym = gdb.lookup_symbol(self.name_)[0]
        except gdb.error: self.sym = gdb.lookup_global_symbol(self.name_)
        if self.sym: return self.symval(self.sym)
        return gdb.parse_and_eval(self.name_)

class Underscore(Expr):
    def __init__(self, n): self.name_ = n
    def eval(self):
        v = underscores[-len(self.name_)]
        yield val2str(v), v

class UnaryBase(Expr):
    def __init__(self, a): self.arg1_ = a
    def name(self): return self.name_.format(self.arg1_.name())
    def eval(self):
        for n,v in self.arg1_.eval():
            yield self.name_.format(n), self.value(v)

class Unary(UnaryBase):
    def __init__(self, n, a, v):
        super (Unary, self).__init__ (a)
        self.name_ = n if '{' in n else n + '{}'
        self.value = v

class Curlies(UnaryBase):
    name_ = "({})"
    def eval(self):
        for n,v in self.arg1_.eval():
            yield val2str(v), v

class BinaryBase(Expr):
    def __init__(self, a1, a2): self.arg1_, self.arg2_ = a1, a2
    def name(self): return self.name_.format(self.arg1_.name(), self.arg2_.name())
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            for n2,v2 in self.arg2_.eval():
                yield self.name_.format(n1, n2), self.value(v1, v2)

class Binary(BinaryBase):
    def __init__(self, a1, n, a2, v):
        super (Binary, self).__init__ (a1, a2)
        self.name_ = n if '{' in n else '{} ' + n + ' {}'
        self.value = v

class Filter(Binary):
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            for n2,v2 in self.arg2_.eval():
                if self.value(v1, v2):
                    yield self.name_.format(n1, n2), v1

class Struct(BinaryBase):
    def __init__(self, a1, n, a2):
        super (Struct, self).__init__ (a1, a2)
        self.name_ = n
    @scoped
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            underscores.append(v1)
            scopes.append(v1)
            for n2,v2 in self.arg2_.eval():
                yield self.name_.format(n1, n2), v2
            scopes.pop()
            underscores.pop()

class StructWalk(BinaryBase):
    name_ = '{}-->{}'
    def path2str(self, path):
        if len(path) == 1: return path[0]
        s, prev, cnt = path[0], path[1], 1
        for m in path[2:] + [None]:
            if m == prev: cnt += 1
            else:
                if cnt == 1: s += '->{}'.format(prev)
                else: s += '-->{}[[{}]]'.format(prev, cnt)
                prev, cnt = m, 1
        return s
    @scoped
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            queue = [ ([n1], v1) ]
            while queue:
                n1, v1 = queue.pop()
                if not v1: continue
                underscores.append(v1)
                scopes.append(v1.dereference())
                yield self.path2str(n1), v1
                l = len(queue)
                for n2,v2 in self.arg2_.eval():
                    queue.insert(l, (n1+[n2], v2))
                scopes.pop()
                underscores.pop()

class TakeNth(BinaryBase):
    name_ = '{}[[{}]]'
    def eval(self):
        for n2,v2 in self.arg2_.eval():
            val = self.arg1_.eval()
            for i in xrange(0,v2): next(val)
            n1, v1 = next(val)
            yield self.name_.format(self.arg1_.name(), n2), v1

class Until(BinaryBase):
    name_ = '{}@{}'
    @scoped
    def eval(self):
        if isinstance(self.arg2_, Literal): f = lambda x,y: x == y
        else: f= lambda x,y: y
        for n1,v1 in self.arg1_.eval():
            underscores.append(v1)
            scopes.append(v1)
            stop, output = False, False
            for n2,v2 in self.arg2_.eval():
                if f(v1, v2): stop = True
                else: output = True
                if stop and output: break
            if output: yield n1, v1
            scopes.pop()
            underscores.pop()
            if stop: break

class URange(UnaryBase):
    def __init__(self, n, a1, to):
        super (URange, self).__init__ (a1)
        self.name_, self.to = n, to
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            for i in xrange(0 if self.to else v1, v1 if self.to else sys.maxsize):
                v = gdb.Value(i).cast(v1.type)
                yield val2str(v), v

class BiRange(BinaryBase):
    name_ = '{}..{}'
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            for n2,v2 in self.arg2_.eval():
                step = 1 if v1 < v2 else -1
                for i in xrange(v1, v2 + step, step):
                    v = gdb.Value(i).cast(v1.type)
                    yield val2str(v), v

class Count(UnaryBase):
    name_ = '#/{}'
    def __init__(self, a): super (Count, self).__init__ (a)
    def eval(self):
        i = 0
        for n,v in self.arg1_.eval(): i +=  1
        yield self.name(), gdb.Value(i)

class LazyGrouping(UnaryBase):
    def __init__(self, n, a, v0, v):
        super (LazyGrouping, self).__init__ (a)
        self.name_, self.init_val, self.add = n + '{}', v0, v
    def eval(self):
        i = self.init_val
        for n,v in self.arg1_.eval():
            i = self.add(i, v)
            if i != self.init_val: break
        yield self.name(), i

class Ternary(Expr):
    def __init__(self, n, a1, a2, a3):
        self.name_, self.arg1_, self.arg2_, self.arg3_= n, a1, a2, a3
    def name(self):
        return self.name_.format(self.arg1_.name(), self.arg2_.name(),
                                 self.arg3_ and self.arg3_.name())
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            for n2,v2 in self.arg2_.eval():
                if self.arg3_:
                    for n3,v3 in self.arg3_.eval():
                        yield self.name_.format(n1, n2, n3), v2 if v1 else v3
                else:
                    if v1: yield self.name_.format(n1, n2), v2

class Alias(BinaryBase):
    name_ = '{} := {}'
    def eval(self):
        for n2,v2 in self.arg2_.eval():
            try: v2 = v2.reference_value()
            except: pass
            aliases[self.arg1_.name()] = (n2, v2)
            yield self.arg1_.name(), v2

class Enumerate(BinaryBase):
    name_ = '{}#{}'
    def eval(self):
        for i, nv1 in enumerate(self.arg1_.eval()):
            aliases[self.arg2_.name()] = (str(i), i)
            yield nv1

class List(Expr):
    def __init__(self, args): self.args_ = args
    def name(self): return ','.join([e.name() for e in self.args_])
    def eval(self):
        for v in self.args_:
            for n2,v2 in v.eval():
                yield n2, v2

class Statement(Expr):
    def __init__(self, args): self.args_ = args
    def name(self): return '; '.join([e.name() for e in self.args_])
    def eval(self):
        for v in self.args_[:-1]:
            for n2,v2 in v.eval(): pass
        for n2,v2 in self.args_[-1].eval():
            yield n2, v2

class Foreach(BinaryBase):
    name_ = '{} => {}'
    @underscored
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            underscores.append(v1)
            for n2,v2 in self.arg2_.eval():
                yield n2, v2
            underscores.pop()

class Call(BinaryBase):
    name_ = '{}({})'
    def eval(self):
        for n1,v1 in self.arg1_.eval():
            args = self.arg2_.args_
            gens = [] + args
            nams = [] + args
            vals = [] + args
            cur = -1
            while True:
                while cur < len(args)-1:
                    cur += 1
                    gens[cur] = args[cur].eval()
                    nams[cur], vals[cur] = next(gens[cur])
                yield self.name_.format(n1, ','.join(nams)), v1(*vals)
                repeat = True
                while repeat and cur >= 0:
                    repeat = False
                    try: nams[cur], vals[cur] = next(gens[cur])
                    except StopIteration:
                        cur -= 1
                        repeat = True
                if cur < 0: break
