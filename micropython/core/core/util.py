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

def dump_json(f, obj) :
    return traverse_json(lambda s : f.write(s), obj)

def traverse_json(ef, obj) :
    obj_type = type(obj)
    if obj_type is dict :
        ef('{')
        i = 0
        for (k, v) in obj.items() :
            if i > 0 :
                ef(',')
            traverse_enquoted(ef, k)
            ef(": ")
            traverse_json(ef, v)
            i = i + 1
        ef('}')
    elif obj_type is list :
        ef('[')
        i = 0
        for e in obj :
            if i > 0 :
                ef(',')
            traverse_json(ef, e)
            i = i + 1
        ef(']')
    elif obj_type is bool :
        ef("true" if obj else "false")
    elif obj_type is str :
        traverse_enquoted(ef, obj)
    else :
        ef(str(obj))

def traverse_enquoted(ef, s) :
    ef('"')
    ef(s) # TODO escape?
    ef('"')

def exists(path) :
    import os
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def save_json(path, obj) :
    import ujson
    with open(path, 'w') as f :
        dump_json(f, obj)
    

def load_json(path) :
    import ujson
    with open(path, 'r') as f :
        return ujson.load(f)

def random_int(lb=0, ub=4924967296) :
    import ustruct
    import os
    return lb + ustruct.unpack("<L", os.urandom(4))[0] % (ub - lb)


def reboot() :
    import machine
    machine.reset()

def localtime_to_string(localtime, timezone="Z") :
    (year, month, day, hour, minute, second, _weekday, _tzinfo) = localtime
    return "%d-%02d-%02dT%02d:%02d:%02d%s" % (year, month, day, hour, minute, second, timezone)

def secs_to_string(secs=None):
    import core
    import utime
    localtime = utime.localtime(secs)
    return localtime_to_string(localtime)

def duration(secs):
    days = 0
    hours = 0
    mins = 0
    one_minute = 60
    one_hour = one_minute * 60
    one_day = one_hour * 24
    if secs > one_day:
        days = secs // one_day
        secs = secs % one_day
    if secs > one_hour:
        hours = secs // one_hour
        secs = secs % one_hour
    if secs > one_minute:
        mins = secs // one_minute
        secs = secs % one_minute
    return days, hours, mins, secs

## adapted from https://gist.github.com/7h3rAm/5603718
def hexdump(src, length=16, sep='.'):
	FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])
	lines = []
	for c in range(0, len(src), length):
		chars = src[c:c+length]
		hex = ' '.join(["%02x" % ord(x) for x in chars])
		if len(hex) > 24:
			hex = "%s %s" % (hex[:24], hex[24:])
		printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or sep) for x in chars])
		lines.append("%08x:  %-*s  |%s|\n" % (c, length*3, hex, printable))
	return ''.join(lines)

def update_dict(d1, d2) :
    d1.update(d2)
    return d1
