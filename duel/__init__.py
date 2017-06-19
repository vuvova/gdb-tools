import gdb
import sys
import traceback

from duel.help import *
from duel import parser, expr

class duel (gdb.Command):
    """Evaluate Duel expressions. Duel is a high level data exploration language"""

    debug = False

    def __init__ (self):
        super (duel, self).__init__ ("duel", gdb.COMMAND_DATA, gdb.COMPLETE_EXPRESSION, True)
        gdb.execute('alias -a dl = duel')

    def invoke (self, arg, from_tty):
        self.init()
        self.invoke(arg, from_tty)

    def init (self):
        gdb.write(HEADER, gdb.STDERR)
        duel.invoke = self.do_command

    def do_command(self, arg, from_tty):
        if arg == "":
            gdb.write(INTRO)
        elif arg in [ '?', 'help' ]:
            gdb.write(HELP)
        elif arg in [ '??', 'longhelp' ]:
            gdb.write(LONGHELP)
        elif arg in [ 'examples' ]:
            gdb.write(EXAMPLES)
        elif arg in [ 'operators' ]:
            gdb.write(OPERATORS)
        elif arg in [ 'debug' ]:
            self.debug = not self.debug
            gdb.write('Duel debug is ' + ['dis', 'en'][self.debug] + 'abled\n')
        elif arg in [ 'aliases' ]:
            if len(expr.aliases) > 0:
                gdb.write("Aliases table:\n")
                for k in sorted(expr.aliases.keys()):
                    n,v=expr.aliases[k]
                    gdb.write("{}: {} = {}\n".format(k, n, expr.val2str(v)))
            else:
                gdb.write("Aliases table empty\n")
        elif arg == 'clear':
            expr.aliases.clear()
            gdb.write("Aliases table cleared\n")
        else:
            try:
                parser.eval(arg)
            except Exception as e:
                gdb.write(str(e)+'\n')
                if self.debug:
                    traceback.print_exc()

duel()
