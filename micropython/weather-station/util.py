'''
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
'''

import machine


def starts_with(str_, prefix) :
    return str_.find(prefix) == 0

def module_to_dict(mod) :
    ret = {}
    for i in dir(mod) :
        if not starts_with(i, '__') :
            ret[i] = getattr(mod, i)
    return ret

def merge_dict(a, b) :
    ret = a.copy()
    ret.update(b)
    return ret

def set_datetime(year, month, day, hour=0, minute=0, second=0) :
    rtc = machine.RTC()
    rtc.datetime((year, month, day, hour, minute, second, 0, 0))

def print_module(module) :
    f = open(module + '.py')
    print("%s" % f.read())
    
def datetimestr() :
    import time
    (year, month, day, hour, minute, second, millis, _tzinfo) = time.localtime()
    return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)

def set_led_error(pin_id=14) :
    import machine
    pin = machine.Pin(pin_id, machine.Pin.OUT)
    pin.high()

def clear_led_error(pin_id=14) :
    import machine
    pin = machine.Pin(pin_id, machine.Pin.OUT)
    pin.low()
