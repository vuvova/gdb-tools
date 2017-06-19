"""a helper for easy creation of gdb pretty-printers"""

import gdb.printing

# in python2 gdb.Value can only be converted to long(), python3 only has int()
try: a=long(1)
except: long=int

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

    def PrettyPrinterWrapperWrapperWrapper(func):

        class PrettyPrinterWrapperWrapper:

            class PrettyPrinterWrapper:
                def __init__(self, prefix, val, cb):
                    self.prefix = prefix
                    self.val = val
                    self.cb = cb
                def to_string(self):
                    return self.prefix + self.cb(self.val)

            def __init__(self, name, cb):
                self.name = name
                self.enabled = True
                self.cb = cb

            def __call__(self, val):
                prefix = ''
                if val.type.code == gdb.TYPE_CODE_PTR:
                    prefix = '({}) {:#08x} '.format(str(val.type), long(val))
                    try: val = val.dereference()
                    except: return None
                valtype=val.type.unqualified()
                if valtype.name == self.name:
                    return self.PrettyPrinterWrapper(prefix, val, self.cb)
                if valtype.strip_typedefs().name == self.name:
                    return self.PrettyPrinterWrapper(prefix, val, self.cb)
                return None

        pp=PrettyPrinterWrapperWrapper(name, func)
        gdb.printing.register_pretty_printer(None, pp, True)
        return func

    if callable(arg):
        return PrettyPrinterWrapperWrapperWrapper(arg)

    return PrettyPrinterWrapperWrapperWrapper
