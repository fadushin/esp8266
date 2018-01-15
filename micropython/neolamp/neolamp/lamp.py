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
import machine
import neopixel
import utime
import logging
import core.util
import core.task


def ensure_colorspec(colorspec) :
    assert type(colorspec) is dict
    assert 'r' in colorspec and ensure_mapo(colorspec['r'])
    assert 'g' in colorspec and ensure_mapo(colorspec['g'])
    assert 'b' in colorspec and ensure_mapo(colorspec['b'])

def ensure_mapo(mapo) :
    assert type(mapo) is dict
    assert 'm' in mapo and  type(mapo['m']) is int and 0 <= mapo['m'] and mapo['m'] < 256
    assert 'a' in mapo and ensure_numeric(mapo['a'], lb=0)
    assert 'p' in mapo and ensure_numeric(mapo['p'], lb=0)
    assert 'o' in mapo and ensure_numeric(mapo['o'], lb=0)
    return True

def ensure_numeric(val, lb=-0xFFFFFFFF, ub=0xFFFFFFFF) :
    (type(val) is int or type(val) is float) and lb <= val and val < ub
    return True


class Lamp(core.task.TaskBase) :

    def __init__(self, pin, num_pixels, colorspec, sleep_ms=100, num_transitions = 10, verbose=False) :
        core.task.TaskBase.__init__(self, sleep_ms, verbose=verbose)
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_pixels)
        self.colorspec = colorspec
        self.prev_colorspec = None
        self.num_transitions = num_transitions
        self.transition_i = 0
        self.initial_tick = None
        self.prev_rgb = None
        self.verbose = verbose
    
    def get_state(self):
        data = []
        for i in range(self.np.n) :
            data.append({
                "r": self.np[i][0],
                "g": self.np[i][1],
                "b": self.np[i][2]
            })
        return data

    def set_colorspec(self, colorspec) :
        if colorspec != self.prev_colorspec :
            self.prev_colorspec = self.colorspec
            self.colorspec = colorspec
            self.transition_i = 1

    def set_np(self, pin, num_pixels) :
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_pixels)
    
    def set_rgb(self, rgb) :
        self.np.fill(rgb)
        self.np.write()

    def pixel_dance(self, count=10):
        for i in range(count):
            for j in range(self.np.n):
                self.set_pixel(j, Lamp.random_pixel(), Lamp.random_pixel(), Lamp.random_pixel())

    def perform(self) :
        current_tick = utime.ticks_ms()
        if not self.initial_tick :
            self.initial_tick = current_tick
        else :
            x = utime.ticks_diff(current_tick, self.initial_tick)
            if x == 0 :
                pass
            elif 0 < x :
                rgb = self.get_color(x)
                if rgb != self.prev_rgb :
                    if self.verbose :
                        logging.info("Lamp: setting color to {} from x={}", rgb, x)
                    self.fill_pixels(rgb)
                    self.prev_rgb = rgb
            else : # wrap around; start over
                logging.info("Lamp: tick wrap")
                self.initial_tick = current_tick
        return True

    def get_color(self, x) :
        if self.prev_colorspec :
            colorspec = Lamp.get_transition(self.prev_colorspec, self.transition_i, self.num_transitions, self.colorspec)
            self.transition_i += 1
            if self.transition_i >= self.num_transitions :
                self.prev_colorspec = None
                self.transition_i = -1
        else :
            colorspec = self.colorspec
        rgb = (
            Lamp.get_color_level(x, colorspec["r"]),
            Lamp.get_color_level(x, colorspec["g"]),
            Lamp.get_color_level(x, colorspec["b"])            
        )
        return rgb
    
    
    @staticmethod
    def get_transition(prev_colorspec, i, n, colorspec) :
        return {
            'r': {
                'm': Lamp.interpolate(i, n, prev_colorspec['r']['m'], colorspec['r']['m']),
                'a': Lamp.interpolate(i, n, prev_colorspec['r']['a'], colorspec['r']['a']),
                'p': Lamp.interpolate(i, n, prev_colorspec['r']['p'], colorspec['r']['p']),
                'o': Lamp.interpolate(i, n, prev_colorspec['r']['o'], colorspec['r']['o'])
            },
            'g': {
                'm': Lamp.interpolate(i, n, prev_colorspec['g']['m'], colorspec['g']['m']),
                'a': Lamp.interpolate(i, n, prev_colorspec['g']['a'], colorspec['g']['a']),
                'p': Lamp.interpolate(i, n, prev_colorspec['g']['p'], colorspec['g']['p']),
                'o': Lamp.interpolate(i, n, prev_colorspec['g']['o'], colorspec['g']['o'])
            },
            'b': {
                'm': Lamp.interpolate(i, n, prev_colorspec['b']['m'], colorspec['b']['m']),
                'a': Lamp.interpolate(i, n, prev_colorspec['b']['a'], colorspec['b']['a']),
                'p': Lamp.interpolate(i, n, prev_colorspec['b']['p'], colorspec['b']['p']),
                'o': Lamp.interpolate(i, n, prev_colorspec['b']['o'], colorspec['b']['o'])
            }
        }

    @staticmethod
    def interpolate(i, n, y1, y2) :
        return y1 + int((i/n)*(y2 - y1))
        
    @staticmethod
    def get_color_level(x, mapo) :
        frequency = (1.0/mapo["p"]) if mapo['p'] != 0 else 1000
        amplitude = mapo["a"]
        magnitude = mapo["m"]
        offset =    mapo["o"]
        # x is measured in milliseconds.  We want frequency to be expressed in hertz (cycles/sec)
        # So for example freq = 1 should reseult in one full sinusoidal (2pi) cycles/sec
        # 0.00628318 ~= 2*math.pi/1000
        y = magnitude + int(amplitude * math.sin(offset + frequency * x * 0.00628318))
        # ensure we are bound below by 0 and above by 255
        return min(max(y, 0), 255)

    def set_pixel(self, j, r, g, b) :
        self.np[j] = (r, g, b)
        self.np.write()

    def fill_pixels(self, rgb) :
        self.np.fill(rgb)
        self.np.write()

    def clear_pixels(self) :
        self.np.fill((0, 0, 0))
        self.np.write()

    @staticmethod
    def random_pixel():
        return core.util.random_int(ub=64)
