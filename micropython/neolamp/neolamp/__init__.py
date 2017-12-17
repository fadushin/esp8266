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
import math
import utime

import logging
import uasyncio

import core.util
import core.task
import uhttpd
import uhttpd.api_handler

import neolamp.api
import neolamp.dev


COLOR_SPECS = {
    "black": {
        "r": {"m": 0, "a": 0,  "p": 1,"o": 0},
        "g": {"m": 0, "a": 0,  "p": 1,"o": 0},
        "b": {"m": 0, "a": 0,  "p": 1,"o": 0}
    },
    "white": {
        "r": {"m": 255, "a": 0,  "p": 1,"o": 0},
        "g": {"m": 255, "a": 0,  "p": 1,"o": 0},
        "b": {"m": 255, "a": 0,  "p": 1,"o": 0}
    },
    "purple_haze": {
        "r": {"m": 64, "a":  5, "p": 10,  "o": 0},
        "g": {"m": 16, "a": 10, "p": 10,  "o": 0},
        "b": {"m": 32, "a": 20, "p": 100, "o": 0}
    },
    "mellow_yellow": {
        "r": {"m": 64, "a":  5, "p": 10,  "o": 0},
        "g": {"m": 32, "a": 20, "p": 100, "o": 0},
        "b": {"m": 8,  "a": 10, "p": 10,  "o": 0}
    },
    "wavy_gravy": {
        "r": {"m": 50, "a":  5, "p": 21,  "o": 0},
        "g": {"m": 80, "a": 40, "p": 10,  "o": 0},
        "b": {"m": 60, "a": 20, "p": 5,   "o": 0}
    },
    "red_alert": {
        "r": {"m": 60, "a": 60, "p":  2,  "o": 0},
        "g": {"m":  0, "a":  0, "p":  1,  "o": 0},
        "b": {"m":  0, "a":  0, "p":  1,  "o": 0}
    }
}

controller = None

def run():
    ##
    ## Set up the NTPd task
    ##
    ntpd = core.task.Ntpd().register()
    ##
    ## Set up the Gc task
    ##
    gcd = core.task.Gcd().register()
    ##
    ## Start the controller and signal we are starting
    ##
    global controller
    controller = neolamp.dev.Controller()
    controller.pixel_dance()
    controller.clear()
    ##
    ## Set up and start the web server
    ##
    #import uhttpd.file_handler
    #import wc.api
    api_handler = uhttpd.api_handler.Handler([
        (['neolamp'], neolamp.api.Handler(controller))
        #, (['system'], wc.api.Handler())
    ])
    #file_handler = uhttpd.file_handler.Handler('/www/neolamp')
    server = uhttpd.Server([
        ('/api', api_handler)
        #,('/', file_handler)
    ], {'max_headers': 50, 'backlog': 10})
    server.run()


def resume() :
    uasyncio.get_event_loop().run_forever()


class NeoLamp(core.task.TaskBase) :

    def __init__(self, np, color_spec, sleep_ms=100, verbose=False) :
        core.task.TaskBase.__init__(self, sleep_ms, verbose=verbose)
        self.np = np
        self.color_spec = color_spec
        self.initial_tick = None
        self.prev_rgb = None
        self.verbose = verbose
    
    def set_color_spec(self, color_spec) :
        self.color_spec = color_spec

    def perform(self) :
        current_tick = utime.ticks_ms()
        if not self.initial_tick :
            self.initial_tick = current_tick
            pass
        else :
            x = utime.ticks_diff(current_tick, self.initial_tick)
            if x == 0 :
                pass
            else :
                if 0 < x :
                    rgb = self.get_color(x)
                    if rgb != self.prev_rgb :
                        if self.verbose :
                            logging.info("Lavalamp: setting color to {} from x={}".format(rgb, x))
                        self.fill_pixels(rgb)
                        self.prev_rgb = rgb
                else : # wrap around; start over
                    logging.info("NeoLamp: tick wrap")
                    self.initial_tick = current_tick
        return True

    def get_color(self, x) :
        rgb = (
            NeoLamp.get_color_level(x, self.color_spec["r"]),
            NeoLamp.get_color_level(x, self.color_spec["g"]),
            NeoLamp.get_color_level(x, self.color_spec["b"])            
        )
        return rgb
        
    @staticmethod
    def get_color_level(x, mapo) :
        frequency = 1.0/mapo["p"]
        amplitude = mapo["a"]
        magnitude = mapo["m"]
        offset =    mapo["o"]
        # x is measured in milliseconds.  We want frequency to be expressed in hertz (cycles/sec)
        # So for example freq = 1 should reseult in one full sinusoidal (2pi) cycles/sec
        # 0.00628318 ~= 2*math.pi/1000
        y = magnitude + int(amplitude * math.sin(offset + frequency * x * 0.00628318))
        # ensure we are bound below by 0 and above by 255
        return core.util.min(core.util.max(y, 0), 255)

    def set_pixel(self, j, r, g, b) :
        self.np[j] = (r, g, b)
        self.np.write()

    def fill_pixels(self, rgb) :
        self.np.fill(rgb)
        self.np.write()

    def clear_pixels(self) :
        self.np.fill((0, 0, 0))
        self.np.write()


class Scheduler(core.task.TaskBase) :

    def __init__(self, lamp, schedules, sleep_ms=1342, verbose=False) :
        core.task.TaskBase.__init__(self, sleep_ms)
        self.lamp = lamp
        self.schedule_pairs = self.create_schedule_pairs(schedules)
        self.verbose = verbose

    def set_schedules(self, schedules) :
        self.schedule_pairs = self.create_schedule_pairs(schedules)

    def perform(self) :
        secs = self.secs_since_midnight()
        schedule_pair = self.current_schedule_pair(secs)
        if schedule_pair :
            (prv, nxt) = schedule_pair
            interpolated = self.interpolate_colorspec(prv, nxt, secs)
            self.lamp.set_color_spec(interpolated)
            if self.verbose :
                logging.info("Interpolated colorspec: {}", interpolated)
        return True

    ##
    ## Internal operations
    ##

    def current_schedule_pair(self, secs) :
        for schedule_pair in self.schedule_pairs :
            if Scheduler.is_between(secs, schedule_pair) :
                return schedule_pair
        return None

    @staticmethod
    def create_schedule_pairs(schedules) :
        ret = []
        for i in range(len(schedules)) :
            if i == 0 :
                pass
            else :
                ret.append((schedules[i-1], schedules[i]))
        return ret

    @staticmethod
    def is_between(secs, schedule_pair) :
        (prv, nxt) = schedule_pair
        return Scheduler.get_secs(prv['time']) <= secs and secs < Scheduler.get_secs(nxt['time'])

    @staticmethod
    def midnight_epoch_secs(secs=None) :
        (year, month, mday, hour, minute, second, wday, yday) = utime.localtime(secs) if secs else utime.localtime()
        return utime.mktime((year, month, mday, 0, 0, 0, wday, yday))

    @staticmethod
    def secs_since_midnight(secs=None) :
        secs = utime.time()
        return secs - Scheduler.midnight_epoch_secs(secs)

    @staticmethod
    def interpolate_colorspec(prv, nxt, x) :
        x1 = Scheduler.get_secs(prv['time'])
        x2 = Scheduler.get_secs(nxt['time'])
        span_x = x2 - x1
        # assert span_x > 0
        prv_color = COLOR_SPECS[prv['color_name']]
        nxt_color = COLOR_SPECS[nxt['color_name']]
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
    def get_secs(time) :
        return time["hour"]*60*60 + time["minute"]*60 + time["second"]

    @staticmethod
    def interpolate(x, span_x, x1, x2, y1, y2) :
        if y1 < y2 :
            return y1 + int(math.sin(math.pi/2 *      (x - x1)/span_x)  * (y2 - y1))
        elif y1 > y2 :
            return y2 + int(math.sin(math.pi/2 * (1 + (x - x1)/span_x)) * (y1 - y2))
        else : ## y1 == y2
            return y1

