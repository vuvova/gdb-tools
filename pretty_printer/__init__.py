"""a helper for easy creation of gdb pretty-printers"""

import gdb.printing

# in python2 gdb.Value can only be converted to long(), python3 only has int()
try: a=long(1)
except: long=int

pp_registry=dict();

class PPWrapper:
    def __init__(self, prefix, val, cb):
        self.prefix = prefix
        self.val = val
        self.cb = cb
    def to_string(self):
        return self.prefix + self.cb(self.val)

class PPDispatcher(gdb.printing.PrettyPrinter):
    def __init__(self):
        super(PPDispatcher, self).__init__('gdb-tools')
    def __call__(self, val):
        prefix = ''
        if val.type.code == gdb.TYPE_CODE_PTR:
            prefix = '({0}) {1:#08x} '.format(str(val.type), long(val))
            try: val = val.dereference()
            except: return None
        valtype=val.type.unqualified()
        try: cb=pp_registry[valtype.name]
        except:
            try: cb=pp_registry[valtype.strip_typedefs().name]
            except: return None
        return PPWrapper(prefix, val, cb)

gdb.printing.register_pretty_printer(None, PPDispatcher(), True)

def PrettyPrinter(arg):
    """@PrettyPrinter decorator.

    With a @PrettyPrinter decorator one only needs to write a function
    that takes gdb.Value as an argument and returns a string to be
    shown by gdb.

    Typical usage:

        @PrettyPrinter
        def some_typename(val):
            <convert val to a string and return it>

    This creates all necessary classes and register a pretty-printer
    for the type "some_typename", be it a typedef'ed type name or
    the real underlying type with all typedef's resolved. It also
    creates a pretty-printer for a pointer to some_typename.

    When a type name is not a valid Python identifier, one can use

        @PrettyPrinter("real complex type name")
        def does_not_matter(val):
            <convert val to a string and return it>
    """
    name = getattr(arg, '__name__', arg)

    def register(func):
        pp_registry[name]=func
        return func

    if callable(arg):
        return register(arg)
    return register
