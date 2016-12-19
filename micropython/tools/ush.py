#
# Copyright (c) dushin.net  All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of dushin.net nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import os
import sys

VERSION = "master"


class Ush:
    def __init__(self, custom_handlers={}):
        ls = Ls()
        self._handlers = {
            'cat': Cat(),
            'cd': Cd(),
            'date': Date(),
            'df': Df(),
            'dump': Dump(),
            'gc': Gc(),
            'ls': ls,
            'll': ls,
            'mem': Mem(),
            'mkfile': Mkfile(),
            'mkdir': Mkdir(),
            'mv': Mv(),
            'ntp': Ntp(),
            'pwd': Pwd(),
            'reboot': Reboot(),
            'rm': Rm(),
            'rmdir': Rmdir(),
            'tree': Tree(),
            'help': Help(self)
        }
        self._handlers.update(custom_handlers)

    def run(self):
        try:
            print("Welcome to ush-{}.  Type 'help' for help.  ^D to exit".format(VERSION))
            while True:
                line = Ush.prompt().strip()
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

    @staticmethod
    def prompt():
        cwd = os.getcwd()
        print("[{}{}] ush$ ".format("/" if not cwd else "", cwd), end="",
              flush=True),
        return input()


class Cmd:
    def __init__(self):
        pass

    @staticmethod
    def remove(el, e):
        el1 = el.copy()
        if e in el1:
            el1.remove(e)
        return el1

    @staticmethod
    def is_dir(path):
        try:
            os.listdir(path)
            return True
        except OSError:
            return False

    @staticmethod
    def exists(path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    @staticmethod
    def matches(d, components):
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

    @staticmethod
    def glob(path):
        if not '*' in path:
            return [path]
        components = path.split("*")
        f = filter(
            lambda d: Cmd.matches(d, components),
            os.listdir()
        )
        ret = []
        for i in f:
            ret.append(i)
        return ret

    @staticmethod
    def traverse(path, visitor, state={}):
        state = visitor.pre(path, state)
        if Cmd.is_dir(path):
            contents = os.listdir(path)
            contents.sort()
            for c in contents:
                new_path = "{}/{}".format(path, c)
                state = Cmd.traverse(new_path, visitor, state=state)
        return visitor.post(path, state)

    @staticmethod
    def append(el, e):
        el1 = el.copy()
        el1.append(e)
        return el1

    @staticmethod
    def read(filename):
        f = open(filename, 'r')
        s = f.read()
        f.close()
        return s


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

    @staticmethod
    def list_dir(d):
        contents = os.listdir(d)
        contents.sort()
        for c in contents:
            Cmd.list_file(c)

    @staticmethod
    def list_file(f):
        stats = os.stat(f)
        print("    {}rwxrwxrwxx {}\t\t{}{}".format(
            "d" if Cmd.is_dir(f) else "-", stats[6], f,
            "/" if Cmd.is_dir(f) else ""))


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
        d = Cmd.glob(args[0])
        if len(d) == 0:
            print("Error!  No Match: {}".format(args[0]))
        elif len(d) > 1:
            print("Error!  Ambiguous: {}".format(args[0]))
        elif not Cmd.exists(d[0]):
            print("Error!  Does not exist: {}".format(d[0]))
        elif not Cmd.is_dir(d[0]):
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
        glob = Cmd.glob(args[0])
        if len(glob) == 0:
            print("Error!  No Match: {}".format(args[0]))
        elif len(glob) > 1:
            print("Error!  Ambiguous: {}".format(args[0]))
        elif not Cmd.exists(glob[0]):
            print("Error!  Does not exist: {}".format(glob[0]))
        elif Cmd.is_dir(glob[0]):
            print("Error!  Directory: {}".format(glob[0]))
        else:
            self.cat(glob[0])

    def help(self):
        return "<file> Catenate a file."

    @staticmethod
    def cat(filename):
        f = open(filename, 'r')
        while True:
            buf = f.read(128)
            if buf:
                sys.stdout.write(buf)
            else:
                break


class Dump(Cmd):
    def __init__(self):
        super().__init__()
        self._buf = bytearray(16)

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: dump [<file>]")
            return
        filename = args[0]
        if not Cmd.exists(filename):
            print("Error!  Does not exist: {}".format(filename))
        elif Cmd.is_dir(filename):
            print("Error!  Directory: {}".format(filename))
        else:
            self.dump(filename)

    def help(self):
        return "<file> Dump a file in hex."

    # adapted from https://gist.github.com/7h3rAm/5603718

    def dump(self, filename):
        if not self._filter:
            self._filter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
        import uio
        f = uio.open(filename)
        total_read = 0
        while True:
            n = f.readinto(self._buf)
            if n:
                self.dump_buf(total_read, self._buf, n)
                total_read += n
            else:
                break

    def dump_buf(self, total_read, buf, n):
        hex_ = ' '.join(["%02x" % x for x in buf[:n]])
        printable = ''.join(["%s" % (x <= 127 and self._filter[x] or '.') for x in buf[:n]])
        pad = 16 - n
        if pad:
            # pad hex with 3 spaces and printable with single spaces
            hex_ = "{}{}".format(hex_, ''.join(["   " for i in range(pad)]))
            printable = "{}{}".format(printable, ''.join(" " for i in range(pad)))
        print("%08x:  %s  |%s|" % (total_read, hex_, printable))


class Mkdir(Cmd):
    def __init__(self):
        super().__init__()

    def handle_command(self, args):
        if len(args) != 1:
            print("Syntax: mkdir <dir>")
            return
        d = args[0]
        if Cmd.exists(d):
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
        if not Cmd.exists(d):
            print("Error!  Does not exist: {}".format(d))
        elif not Cmd.is_dir(d):
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
        if not Cmd.is_dir(path):
            os.remove(path)
        return state

    def post(self, path, state):
        if Cmd.is_dir(path):
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
        if not Cmd.exists(path):
            print("Error!  Does not exist: {}".format(path))
        elif Cmd.is_dir(path) and not "-r" in args0:
            print("Error!  Directory: {}".format(path))
        elif Cmd.is_dir(path) and "-r" in args0:
            Cmd.traverse(path, self._visitor)
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
        if not Cmd.exists(a):
            print("Error!  Source does not exist: {}".format(a))
        elif Cmd.exists(b):
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
            args1 = Cmd.remove(args, "-s")
            if len(args1) < 1:
                print("Syntax: [-s secs]")
            else:
                Cmd.set_datetime(int(args1[0]))
        print(self.get_datetime())

    def help(self):
        return "[-s secs] Print (or set) the date."

    @staticmethod
    def set_datetime(secs) :
        import utime
        import machine
        tm = utime.localtime(secs)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)

    @staticmethod
    def get_datetime() :
        import time
        year, month, day, hour, minute, second, millis, _tzinfo = time.localtime()
        return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)



class DateTimeCmd(Cmd):
    def __init__(self):
        super().__init__()

    @staticmethod
    def datetime_str(localtime) :
        (year, month, day, hour, minute, second, millis, _tzinfo) = localtime
        return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)

    @staticmethod
    def get_localtime(raw=False):
        import utime
        localtime = utime.localtime()
        if raw:
            return utime.mktime(localtime)
        else:
            return DateTimeCmd.datetime_str(localtime)

    @staticmethod
    def get_datetime_from_secs(secs):
        import utime
        tm = utime.localtime(secs)
        return DateTimeCmd.datetime_str(tm)


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

    def help(self):
        return "[-s secs] [-r] Print (or set) the date (-r to print raw time in secs)."

    @staticmethod
    def set_datetime(secs):
        import utime
        import machine
        tm = utime.localtime(secs)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)


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
                print(DateTimeCmd.get_datetime_from_secs(secs))

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
