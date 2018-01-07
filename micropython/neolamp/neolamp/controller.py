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

import uasyncio
import logging

import core.util
import core.task
import neolamp.lamp
import neolamp.scheduler
import neolamp.tz

class Controller :

    MODE_OFF="off"
    MODE_LAMP="lamp"
    MODE_SCHEDULER="scheduler"
    MODE_TEST="test"
    DEFAULT_CONFIG_PATH="/neolamp_default.json"
    
    def __init__(self, path='/neolamp.json'):
        self.path = path
        self.config = core.util.load_json(path if core.util.exists(path) else Controller.DEFAULT_CONFIG_PATH)
        self.gcd = core.task.Gcd().register()
        self.ntpd = core.task.Ntpd().register()
        self.tzd = neolamp.tz.Timezoned().register()
        self.lamp = neolamp.lamp.Lamp(self.config["pin"], self.config["num_pixels"], self.config['color_specs']["black"]).register()
        self.clear()
        self.scheduler = neolamp.scheduler.Scheduler(self.lamp, self.tzd, [], self.config['color_specs']).register()
        self.set_mode(self.config['mode'], init=True)
    
    def set_np(self, pin=None, num_pixels=None) :
        if pin or num_pixels :
            self.config["pin"] = int(pin) if pin else 2
            self.config["num_pixels"] = int(num_pixels) if num_pixels else 1
            self.lamp.set_np(self.config["pin"], self.config["num_pixels"])
            logging.info("Setting pin to {} and num_pixels to {}", self.config["pin"], self.config["num_pixels"])
            self.save_config()
    
    def set_mode(self, mode, init=False) :
        assert mode in [Controller.MODE_OFF, Controller.MODE_LAMP, Controller.MODE_SCHEDULER]
        current_mode = self.config['mode']
        if mode == current_mode and not init:
            return
        if mode == Controller.MODE_OFF :
            self.lamp.disable()
            self.scheduler.disable()
            self.clear(5)
        else :
            self.lamp.enable()
        if mode == Controller.MODE_LAMP :
            color_name = self.config[mode]['color_name']
            color_spec = self.config['color_specs'][color_name]
            self.lamp.set_colorspec(color_spec)
            self.scheduler.disable()
        if mode == Controller.MODE_SCHEDULER :
            schedules = self.config[mode]['schedules']
            self.clear(5)
            self.scheduler.set_schedules(schedules)
            self.scheduler.enable()
        if not init :
            self.config['mode'] = mode
            logging.info("Mode set to {}", mode)
            self.save_config()

    def set_color(self, rgb) :
        self.lamp.set_rgb(rgb)
        logging.info("Color set to {}", rgb)

    def get_color(self) :
        return self.lamp.get_state()

    def set_colorspec(self, name, colorspec) :
        neolamp.lamp.ensure_colorspec(colorspec)
        self.config['color_specs'].update({name: colorspec})
        logging.info("colorspec {} set", name)
        self.save_config()

    def delete_colorspec(self, name) :
        if name in self.config['color_specs'] :
            del self.config['color_specs'][name]
            logging.info("colorspec {} deleted", name)
            self.save_config()
        else :
            raise RuntimeError("No such colorspec: {}".format(name))

    def set_color_name(self, color_name) :
        assert color_name in self.config['color_specs']
        self.config[Controller.MODE_LAMP]['color_name'] = color_name
        color_spec = self.config['color_specs'][color_name]
        self.lamp.set_colorspec(color_spec)
        logging.info("Color set to {}", color_name)
        self.save_config()

    def update_schedule(self, name, schedule) :
        neolamp.scheduler.ensure_schedule(schedule)
        self.config[Controller.MODE_SCHEDULER]['schedules'].update({name : schedule})
        self.scheduler.set_schedules(self.config[Controller.MODE_SCHEDULER]['schedules'])
        logging.info("Schedule added: {}", name)
        self.save_config()

    def delete_schedule(self, name) :
        if name in self.config[Controller.MODE_SCHEDULER]['schedules'] :
            del self.config[Controller.MODE_SCHEDULER]['schedules'][name]
            self.scheduler.set_schedules(self.config[Controller.MODE_SCHEDULER]['schedules'])
            logging.info("Schedule deleted: {}", name)
            self.save_config()
        else :
            raise RuntimeError("No such schedule: {}".format(name))
    
    def save_config(self) :
        core.util.save_json(self.path, self.config)
        logging.info("Configuration saved to {}", self.path)
                    
    def reboot(self, delay_ms=1342) :
        loop = uasyncio.get_event_loop()
        logging.info("Going down for reboot in {}ms ...", delay_ms)
        loop.call_later_ms(delay_ms, core.util.reboot)
    
    def reset(self) :
        if core.util.exists(self.path) :
            os.remove(self.path)
        logging.info("Neolamp reset to default settings.")
        self.reboot()
    
    def get_stats(self) :
        return {
            'gcd': self.gcd.stats(),
            'ntpd': self.ntpd.stats(),
            'lamp': self.lamp.stats(),
            'scheduler': self.scheduler.stats()
        }
            
    def clear(self, num_calls=5) :
        for i in range(num_calls) :
            self.lamp.clear_pixels()

    def pixel_dance(self, count=10):
        self.lamp.pixel_dance(count)
