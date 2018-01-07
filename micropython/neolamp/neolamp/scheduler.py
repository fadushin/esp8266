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

import math
import utime

import logging
import uasyncio

import core.util
import core.task

def ensure_schedule(schedule) :
    assert type(schedule) is dict
    assert 'dow' in schedule
    ensure_dow(schedule['dow'])
    assert 'seq' in schedule
    ensure_seq(schedule['seq'])

def ensure_dow(dow) :
    assert type(dow) is list
    assert all(map(lambda i : type(i) is int and i in [1,2,3,4,5,6,7], dow))

def ensure_seq(seq) :
    assert type(seq) is list
    assert all(map(lambda e : ensure_element(e), seq))

def ensure_element(e) :
    assert type(e) is dict
    assert 'time' in e
    ensure_time(e['time'])
    assert 'color_name' in e
    ensure_color_name(e['color_name'])
    return True

def ensure_time(t) :
    assert type(t) is dict
    assert 'h' in t and type(t['h']) is int and 0 <= t['h'] and t['h'] <= 23
    assert 'm' in t and type(t['m']) is int and 0 <= t['m'] and t['m'] <= 59
    assert 's' in t and type(t['s']) is int and 0 <= t['s'] and t['s'] <= 59

def ensure_color_name(color_name) :
    assert type(color_name) is str



class Scheduler(core.task.TaskBase) :

    def __init__(self, lamp, tzd, schedules, color_specs, sleep_ms=1342, verbose=False) :
        core.task.TaskBase.__init__(self, sleep_ms)
        self.lamp = lamp
        self.tzd = tzd
        self.schedules = schedules
        self.color_specs = color_specs
        self.verbose = verbose
        self.current_schedule_name = None

    def set_schedules(self, schedules) :
        self.schedules = schedules

    def perform(self) :
        localtime = self.get_localtime()
        secs = self.secs_since_midnight(localtime)
        (_year, _month, _mday, _hour, _minute, _second, wday, _yday) = localtime
        seq_pair = self.current_seq_pair(secs, wday + 1)
        if seq_pair :
            (prv, nxt) = seq_pair
            interpolated = self.interpolate_colorspec(prv, nxt, secs)
            self.lamp.set_colorspec(interpolated)
            if self.verbose :
                logging.info("Interpolated colorspec: {}", interpolated)
        else :
            self.lamp.set_colorspec(self.color_specs['black'])
        return True
    
    

    ##
    ## Internal operations
    ##
    
    def get_localtime(self) :
        secs = utime.time()
        secs += self.tzd.get_offset_hours() * 60 * 60
        return utime.localtime(secs)

    def current_seq_pair(self, secs, dow) :
        for (schedule_name, schedule) in self.schedules.items() :
            if dow in schedule['dow'] :
                seq = schedule['seq']
                i = Scheduler.find_index_in_range(secs, seq)
                if i == -1 :
                    return None
                else :
                    if self.current_schedule_name != schedule_name :
                        logging.info("Entering schedule {}", schedule_name)
                        self.current_schedule_name = schedule_name
                    return (seq[i], seq[i+1])
        if self.current_schedule_name :
            logging.info("Leaving schedule {}", self.current_schedule_name)
            self.current_schedule_name = None
            # set last here?
        return None

    @staticmethod
    def find_index_in_range(secs, seq) :
        n = len(seq)
        for i in range(n) :
            seq_i = seq[i]
            seq_i_secs = Scheduler.get_secs(seq_i['time'])
            if secs < seq_i_secs :
                return -1
            elif i < n - 1 : # and seq_i <= secs
                seq_iplus1 = seq[i+1]
                seq_iplus1_secs = Scheduler.get_secs(seq_iplus1['time'])
                if secs < seq_iplus1_secs :
                    return i
            i += 1
        return -1

    @staticmethod
    def secs_since_midnight(localtime) :
        secs = utime.mktime(localtime)
        return secs - Scheduler.midnight_epoch_secs(localtime)

    @staticmethod
    def midnight_epoch_secs(localtime) :
        (year, month, mday, hour, minute, second, wday, yday) = localtime
        return utime.mktime((year, month, mday, 0, 0, 0, wday, yday))

    @staticmethod
    def get_secs(time) :
        return time["h"]*60*60 + time["m"]*60 + time["s"]

    def interpolate_colorspec(self, prv, nxt, x) :
        x1 = Scheduler.get_secs(prv['time'])
        x2 = Scheduler.get_secs(nxt['time'])
        span_x = x2 - x1
        # assert span_x > 0
        prv_color = self.color_specs[prv['color_name']]
        nxt_color = self.color_specs[nxt['color_name']]
        return {
            'r': {
                'p': Scheduler.interpolate(x, span_x, x1, x2, prv_color['r']['p'], nxt_color['r']['p']),
                'a': Scheduler.interpolate(x, span_x, x1, x2, prv_color['r']['a'], nxt_color['r']['a']),
                'm': Scheduler.interpolate(x, span_x, x1, x2, prv_color['r']['m'], nxt_color['r']['m']),
                'o': Scheduler.interpolate(x, span_x, x1, x2, prv_color['r']['o'], nxt_color['r']['o'])
            },
            'g': {
                'p': Scheduler.interpolate(x, span_x, x1, x2, prv_color['g']['p'], nxt_color['g']['p']),
                'a': Scheduler.interpolate(x, span_x, x1, x2, prv_color['g']['a'], nxt_color['g']['a']),
                'm': Scheduler.interpolate(x, span_x, x1, x2, prv_color['g']['m'], nxt_color['g']['m']),
                'o': Scheduler.interpolate(x, span_x, x1, x2, prv_color['g']['o'], nxt_color['g']['o'])
            },
            'b': {
                'p': Scheduler.interpolate(x, span_x, x1, x2, prv_color['b']['p'], nxt_color['b']['p']),
                'a': Scheduler.interpolate(x, span_x, x1, x2, prv_color['b']['a'], nxt_color['b']['a']),
                'm': Scheduler.interpolate(x, span_x, x1, x2, prv_color['b']['m'], nxt_color['b']['m']),
                'o': Scheduler.interpolate(x, span_x, x1, x2, prv_color['b']['o'], nxt_color['b']['o'])
            }
        }

    @staticmethod
    def interpolate(x, span_x, x1, x2, y1, y2) :
        if y1 < y2 :
            return y1 + int(math.sin(math.pi/2 *      (x - x1)/span_x)  * (y2 - y1))
        elif y1 > y2 :
            return y2 + int(math.sin(math.pi/2 * (1 + (x - x1)/span_x)) * (y1 - y2))
        else : ## y1 == y2
            return y1

