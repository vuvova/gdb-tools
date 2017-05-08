import gdb.printing

# in python2 gdb.Value can only be converted to long(), python3 only has int()
try: a=long(1)
except: long=int

def PrettyPrinter(arg):

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
