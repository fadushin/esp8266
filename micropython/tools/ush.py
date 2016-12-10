"""
Copyright (c) dushin.net  All Rights Reserved

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of dushin.net nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import sys


class Ush:
    def __init__(self):
        ls = Ls()
        self._handlers = {
            'ls': ls,
            'll': ls,
            'cd': Cd(),
            'pwd': Pwd(),
            'cat': Cat(),
            'mkdir': Mkdir(),
            'mkfile': Mkfile(),
            'rmdir': Rmdir(),
            'rm': Rm(),
            'mv': Mv(),
            'df': Df(),
            'mem': Mem(),
            'gc': Gc(),
            'reboot': Reboot(),
            'tree': Tree(),
            'dump': Dump(),
            'date': Date(),
            'ntp': Ntp(),
            'help': Help(self)
        }

    def run(self):
        try:
            print("Welcome to ussh pre-0.1.  Type 'help' for help")
            while True:
                line = self.prompt().strip()
                if line:
                    tokens = line.split()
                    cmd = tokens[0]
                    if cmd in self._handlers:
                        handler = self._handlers[cmd]
                        try:
                            handler.handle_command(tokens[1:])
                        except Exception as e:
                            sys.print_exception(e)
                    else:
                        print("Unknown command: {}".format(cmd))
        except Exception as e:
            print(e)

    def prompt(self):
        cwd = os.getcwd()
        print("[{}{}] ush$ ".format("/" if not cwd else "", cwd), end="",
              flush=True),
        return input()


class Cmd:
    def __init__(self):
        pass

    def remove(self, el, e):
        el1 = el.copy()
        if e in el1:
            el1.remove(e)
        return el1

    def is_dir(self, path):
        try:
            os.listdir(path)
            return True
        except OSError:
            return False

    def exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def matches(self, d, components):
        i = 0
        n = len(components)
        for c in components:
            if i == 0 and not d.startswith(c):
                return False
            if i == n - 1 and not d.endswith(c):
                return False
            else:
                idx = d.find(c)
                if idx == -1:
                    return False
                d = d[idx:]
            i += 1
        return True

    def glob(self, path):
        if not '*' in path:
            return [path]
        components = path.split("*")
        f = filter(
            lambda d: self.matches(d, components),
            os.listdir()
        )
        ret = []
        for i in f:
            ret.append(i)
        return ret

    def traverse(self, path, visitor, state={}):
        state = visitor.pre(path, state)
        if self.is_dir(path):
            contents = os.listdir(path)
            contents.sort()
            for c in contents:
                new_path = "{}/{}".format(path, c)
                state = self.traverse(new_path, visitor, state=state)
        return visitor.post(path, state)

    def append(self, el, e):
        el1 = el.copy()
        el1.append(e)
        return el1


class Ls(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        contents = []
        if args == []:
            contents = os.listdir()
        else:
            for file in args:
                el = self.glob(file)
                for e in el:
                    contents.append(e)
        contents.sort()
        for i in contents:
            self.list_file(i)

    def list_dir(self, d):
        contents = os.listdir(d)
        contents.sort()
        for c in contents:
            self.list_file(c)

    def list_file(self, f):
        stats = os.stat(f)
        print("    {}rwxrwxrwxx {}\t\t{}{}".format(
            "d" if self.is_dir(f) else "-", stats[6], f,
            "/" if self.is_dir(f) else ""))


    def help(self):
        return "[<pattern>] List files or directories.  No pattern lists all files in the CWD."


class Cd(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) == 0:
            os.chdir('/')
            return
        elif len(args) != 1:
            print("Syntax: cd [<dir>]")
            return
        d = self.glob(args[0])
        if len(d) == 0:
            print("Error!  No Match: {}".format(args[0]))
        elif len(d) > 1:
            print("Error!  Ambiguous: {}".format(args[0]))
        elif not self.exists(d[0]):
            print("Error!  Does not exist: {}".format(d[0]))
        elif not self.is_dir(d[0]):
            print("Error!  Not a directory: {}".format(d[0]))
        else:
            os.chdir(d[0])

    def help(self):
        return "[<pattern>] Change directory.  No pattern changes to '/'"


class Pwd(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, _args):
        cwd = os.getcwd()
        print("{}{}".format("/" if not cwd else "", cwd))

    def help(self):
        return "Print the CWD."


class Cat(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: cat [<file>]")
            return
        glob = self.glob(args[0])
        if len(glob) == 0:
            print("Error!  No Match: {}".format(args[0]))
        elif len(glob) > 1:
            print("Error!  Ambiguous: {}".format(args[0]))
        elif not self.exists(glob[0]):
            print("Error!  Does not exist: {}".format(glob[0]))
        elif self.is_dir(glob[0]):
            print("Error!  Directory: {}".format(glob[0]))
        else:
            self.cat(glob[0])

    def cat(self, filename):
        f = open(filename, 'r')
        while True:
            buf = f.read(128)
            if buf:
                sys.stdout.write(buf)
            else:
                break

    def help(self):
        return "<file> Catenate a file."


class Dump(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: dump [<file>]")
            return
        filename = args[0]
        if not self.exists(filename):
            print("Error!  Does not exist: {}".format(filename))
        elif self.is_dir(filename):
            print("Error!  Directory: {}".format(filename))
        else:
            self.dump(self.read(filename))

    ## adapted from https://gist.github.com/7h3rAm/5603718
    def dump(self, src, length=16, sep='.'):
        FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])
        for c in range(0, len(src), length):
            chars = src[c:c+length]
            hex = ' '.join(["%02x" % ord(x) for x in chars])
            if len(hex) > 24:
                hex = "%s %s" % (hex[:24], hex[24:])
            printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or sep) for x in chars])
            print("%08x:  %-*s  |%s|\n" % (c, length*3, hex, printable))

    def read(self, filename):
        f = open(filename, 'r')
        s = f.read()
        f.close()
        return s

    def help(self):
        return "<file> Dump a file in hex."


class Mkdir(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: mkdir <dir>")
            return
        d = args[0]
        if self.exists(d):
            print("Error!  Already exists: {}".format(d))
        else:
            os.mkdir(d)

    def help(self):
        return "<dirname> Make a directory."


class Mkfile(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: mkfile <file>")
            return
        d = args[0]
        print("Enter '.' on an empty line to terminate")
        f = open(d, 'w')
        while True:
            line = input()
            if line == ".":
                break
            f.write("{}\n".format(line))
        f.close()

    def help(self):
        return "<file> Make a file."


class Rmdir(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: rmdir [<dir>]")
            return
        d = args[0]
        if not self.exists(d):
            print("Error!  Does not exist: {}".format(d))
        elif not self.is_dir(d):
            print("Error!  Not a directory: {}".format(d))
        elif os.listdir(d):
            print("Error!  Directory not empty: {}".format(d))
        else:
            os.rmdir(d)

    def help(self):
        return "<dirname> Remove an empty directory"


class RemoveVisitor(Cmd):
    def __init__(self):
        super().__init__()

    def pre(self, path, state):
        if not self.is_dir(path):
            os.remove(path)
        return state

    def post(self, path, state):
        if self.is_dir(path):
            os.rmdir(path)
        return state


class Rm(Cmd):
    def __init__(self):
        super().__init__()
        self._visitor = RemoveVisitor()

    def handle_command(self, args0):
        args = self.remove(args0, "-r")
        if len(args) != 1:
            print("Syntax: rm [-r] [<dir>]")
            return
        path = args[0]
        if not self.exists(path):
            print("Error!  Does not exist: {}".format(path))
        elif self.is_dir(path) and not "-r" in args0:
            print("Error!  Directory: {}".format(path))
        elif self.is_dir(path) and "-r" in args0:
            self.traverse(path, self._visitor)
        else:
            os.remove(path)

    def help(self):
        return "[-r] <file> Remove a file (-r to recursively remove a directory)."


class Mv(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 2:
            print("Syntax: mv <a> <b>")
            return
        a = args[0]
        b = args[1]
        if not self.exists(a):
            print("Error!  Source does not exist: {}".format(a))
        elif self.exists(b):
            print("Error!  Target exists: {}".format(b))
        else:
            os.rename(a, b)

    def help(self):
        return "<src> <tgt> Move a file or directory."


class Df(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, _args):
        stats = os.statvfs('/')
        frsize = stats[1]
        blocks = stats[2]
        bavail = stats[4]
        capacity = blocks * frsize
        free = bavail * frsize
        print("    mount    capacity\tfree\tusage")
        print("    /        {}\t{}\t{}%".format(capacity, free, int(
            ((capacity - free) / capacity) * 100.0)))

    def help(self):
        return "Print disk usage statistics."


class Mem(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        import gc
        mem_alloc = gc.mem_alloc()
        mem_free = gc.mem_free()
        capacity = mem_alloc + mem_free
        print("    capacity\tfree\tusage")
        print("    {}\t{}\t{}%".format(capacity, mem_free, int(
            ((capacity - mem_free) / capacity) * 100.0)))
        if "-i" in args:
            import micropython
            micropython.mem_info(1)

    def help(self):
        return "[-i] Print memory statistics."


class Gc(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, _args):
        import gc
        gc.collect()

    def help(self):
        return "Run the garbage collector."


class Reboot(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, _args):
        import machine
        machine.reset()

    def help(self):
        return "Reboot the device."


class PrintVisitor:
    def __init__(self):
        pass

    def pre(self, path, state):
        print(path)
        return state

    def post(self, path, state):
        return state


class Tree(Cmd):
    def __init__(self):
        super().__init__()
        self._visitor = PrintVisitor()

    def handle_command(self, args):
        path = args[0] if len(args) > 0 else "."
        self.traverse(path, self._visitor)

    def help(self):
        return "[<path>] Print the directory tree from <path>, or CWD if unspecified."


class Date(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if "-s" in args:
            args1 = self.remove(args, "-s")
            if len(args1) < 1:
                print("Syntax: [-s secs]")
            else:
                self.set_datetime(int(args1[0]))
        print(self.get_datetime())

    def set_datetime(self, secs) :
        import utime
        import machine
        tm = utime.localtime(secs)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)

    def get_datetime(self) :
        import time
        (year, month, day, hour, minute, second, millis, _tzinfo) = time.localtime()
        return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)

    def help(self):
        return "[-s secs] Print (or set) the date."



class DateTimeCmd(Cmd):
    def __init__(self):
        super().__init__()

    def datetime_str(self, localtime) :
        (year, month, day, hour, minute, second, millis, _tzinfo) = localtime
        return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)

    def get_localtime(self, raw=False):
        import utime
        if raw :
            return utime.mktime(utime.localtime())
        else:
            return self.datetime_str(utime.localtime())


class Date(DateTimeCmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if "-s" in args:
            args1 = self.remove(args, "-s")
            if len(args1) < 1:
                print("Syntax: [-s secs]")
            else:
                self.set_datetime(int(args1[0]))
        print(self.get_localtime(True if "-r" in args else False))

    def set_datetime(self, secs):
        import utime
        import machine
        tm = utime.localtime(secs)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)

    def help(self):
        return "[-s secs] [-r] Print (or set) the date (-r to print raw time in secs)."


class Ntp(DateTimeCmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        import ntptime
        if "-s" in args:
            ntptime.settime()
            print(self.get_localtime())
        else:
            secs = ntptime.time()
            if "-r" in args:
                print(secs)
            else:
                print(self.get_datetime_from_secs(secs))

    def get_datetime_from_secs(self, secs):
        import utime
        tm = utime.localtime(secs)
        return self.datetime_str(tm)

    def help(self):
        return "[-s] [-r] Print (or set) the date via NTP (-r to print raw time in secs).  Requires network access"


class Help(Cmd):
    def __init__(self, ush):
        super().__init__()
        self._ush = ush

    def handle_command(self, _args):
        keylist = self.list_keys()
        keylist.sort()
        for key in keylist:
            print("{}\t{}".format(key, self._ush._handlers[key].help()))

    def help(self):
        return "Print this help."

    def list_keys(self):
        ret = []
        for key in self._ush._handlers.keys():
            ret.append(key)
        return ret


def run():
    Ush().run()
