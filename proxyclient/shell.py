#!/usr/bin/env python3

import atexit, serial, os, struct, code, traceback, readline, rlcompleter
from proxy import *
import __main__
import builtins
from proxyutils import *
from utils import *
import sysreg

class HistoryConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.m1n1-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.histfile = histfile
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass

    def save_history(self):
        readline.set_history_length(10000)
        readline.write_history_file(self.histfile)

    def showtraceback(self):
        type, value, tb = sys.exc_info()
        traceback.print_exception(type, value, tb)

class ExitConsole(SystemExit):
    pass

def run_shell(locals, msg=None, exitmsg=None):
    saved_display = sys.displayhook
    try:
        def display(val):
            try:
                global mon
                mon.poll()
            except NameError:
                pass
            if isinstance(val, int):
                builtins._ = val
                print(hex(val))
            elif callable(val):
                val()
            else:
                saved_display(val)

        sys.displayhook = display

        # convenience
        locals["h"] = hex
        locals["sysreg"] = sysreg

        if "proxy" in locals and "p" not in locals:
            locals["p"] = locals["proxy"]
        if "utils" in locals and "u" not in locals:
            locals["u"] = locals["utils"]

        for obj in ("iface", "p", "u"):
            if obj in locals:
                for attr in dir(locals[obj]):
                    if attr not in locals:
                        v = getattr(locals[obj], attr)
                        if callable(v):
                            locals[attr] = v

        for attr in dir(sysreg):
            locals[attr] = getattr(sysreg, attr)

        try:
            con = HistoryConsole(locals)
            con.interact(msg, exitmsg)
        except ExitConsole as e:
            if len(e.args):
                return e.args[0]
            else:
                return
        finally:
            con.save_history()

    finally:
        sys.displayhook = saved_display

if __name__ == "__main__":
    from setup import *
    locals = __main__.__dict__

    from tgtypes import *

    run_shell(locals, msg="Have fun!")
