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

import utime

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


def vcc():
    import machine
    mv = machine.ADC(0)
    return mv.read() * 1.024

def gcollect():
    import gc
    gc.collect()

def ush():
    import ush
    ush.run()


def wc():
    import uhttpd
    import uhttpd.file_handler
    import uhttpd.api_handler
    import api

    api_handler = uhttpd.api_handler.Handler([
        #([], api.APIHandler())
        (['system'], api.SystemAPIHandler()),
        (['memory'], api.MemoryAPIHandler()),
        (['flash'], api.FlashAPIHandler()),
        (['network'], api.NetworkAPIHandler())
    ])
    file_handler = uhttpd.file_handler.Handler(block_size=256)
    server = uhttpd.Server([
        ('/api', api_handler),
        ('/', file_handler)
    ], {'max_headers': 50, 'backlog': 10})
    server.run()

start_time = utime.time()

def uptime():
    current_secs = utime.time()
    secs = current_secs - start_time
    return duration(secs)

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

