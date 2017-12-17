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

import core.util
import utime
import os

def ls() :
    files = os.listdir()
    files.sort()
    for f in files :
        stats = os.stat(f)
        print("    {}rwxrwxrwxx {}\t\t{}{}".format(
            "d" if _is_dir(f) else "-", stats[6], f,
            "/" if _is_dir(f) else ""))

def mkdir(path) :
    if _exists(path):
        print("Error!  Already exists: {}".format(path))
    else:
        os.mkdir(path)

def mkfile(path) :
    f = open(path, 'w')
    print("Enter '.' on an empty line to terminate")
    while True:
        line = input()
        if line == ".":
            break
        f.write("{}\n".format(line))
    f.close()

def rm(path) :
    if not _exists(path):
        print("Error!  Does not exist: {}".format(path))
    elif _is_dir(path):
        print("Error!  Directory: {}".format(path))
    else:
        os.remove(path)

def rmdir(path) :
    if not _exists(path):
        print("Error!  Does not exist: {}".format(path))
    elif not _is_dir(path):
        print("Error!  Not a directory: {}".format(path))
    elif os.listdir(path):
        print("Error!  Directory not empty: {}".format(path))
    else:
        os.rmdir(path)

def cd(path="/") :
    os.chdir(path)
    pwd()

def pwd() :
    cwd = os.getcwd()
    print("{}{}".format("/" if not cwd else "", cwd))

def cat(path) :
    import sys
    f = open(path, 'r')
    while True:
        buf = f.read(128)
        if buf:
            sys.stdout.write(buf)
        else:
            break

def reboot():
    import machine
    machine.reset()

def mem(level=None):
    import gc
    mem_alloc = gc.mem_alloc()
    mem_free = gc.mem_free()
    capacity = mem_alloc + mem_free
    print("    capacity\tfree\tusage")
    print("    {}\t{}\t{}%".format(capacity, mem_free, int(
        ((capacity - mem_free) / capacity) * 100.0)))
    if level:
        import micropython
        micropython.mem_info(level)

def df():
    import os
    stats = os.statvfs('/')
    frsize = stats[1]
    blocks = stats[2]
    bavail = stats[4]
    capacity = blocks * frsize
    free = bavail * frsize
    print("    mount    capacity\tfree\tusage")
    print("    /        {}\t{}\t{}%".format(capacity, free, int(
        ((capacity - free) / capacity) * 100.0)))

def gcollect():
    import gc
    gc.collect()

start_time = utime.time()
def uptime():
    current_secs = utime.time()
    secs = current_secs - start_time
    return core.util.duration(secs)

def ifconfig():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.active() :        
        (ip, subnet, gateway, dns) = sta_if.ifconfig()
        print("Station:\n\tip: {}\n\tsubnet: {}\n\tgateway: {}\n\tdns: {}".format(ip, subnet, gateway, dns))
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active() :        
        (ip, subnet, gateway, dns) = ap_if.ifconfig()
        print("Access Point:\n\tip: {}\n\tsubnet: {}\n\tgateway: {}\n\tdns: {}".format(ip, subnet, gateway, dns))

def date(secs=False):
    localtime = utime.localtime()
    if secs:
        print(utime.mktime(localtime))
    else:
        print(core.localtime_to_string(localtime))

def ntpupdate():
    import ntptime
    ntptime.settime()

def run_event_loop():
    import uasyncio
    print("Running event loop... (^C to exit)")
    uasyncio.get_event_loop().run_forever()
    
def _is_dir(path):
    try:
        os.listdir(path)
        return True
    except OSError:
        return False

def _exists(path) :
    try:
        os.stat(path)
        return True
    except OSError:
        return False
