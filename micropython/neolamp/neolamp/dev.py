import os
import utime
import math
import machine
import neopixel

import uasyncio
import logging

import core.util
import neolamp


class Controller :

    MODE_OFF="off"
    MODE_NEOLAMP="neolamp"
    MODE_SCHEDULE="scheduler"
    MODE_TEST="test"
    DEFAULT_CONFIG_PATH="/neolamp_default.json"
    
    def __init__(self, path='/neolamp.json'):
        self.path = path
        self.config = core.util.load_json(path if core.util.exists(path) else Controller.DEFAULT_CONFIG_PATH)
        self.np = Controller.create_neopixel(self.config["pin"], self.config["num_pixels"])
        self.lamp = neolamp.NeoLamp(self.np, neolamp.COLOR_SPECS["black"]).register()
        self.clear()
        self.scheduler = neolamp.Scheduler(self.lamp, []).register()
        self.set_mode(self.config['mode'], init=True)
    
    def set_mode(self, mode, init=False) :
        current_mode = self.config['mode']
        if mode == current_mode and not init:
            return
        if mode == Controller.MODE_OFF :
            self.lamp.disable()
            self.scheduler.disable()
            self.clear(5)
        else :
            self.lamp.enable()
        if mode == Controller.MODE_NEOLAMP :
            color_name = self.config[mode]['color_name']
            color_spec = neolamp.COLOR_SPECS[color_name]
            logging.info("Setting NeoLamp color to {}", color_name)
            self.lamp.set_color_spec(color_spec)
            self.scheduler.disable()
        if mode == Controller.MODE_SCHEDULE :
            schedules = self.config[mode]['schedules']
            logging.info("Setting schedules to {}", schedules)
            self.scheduler.set_schedules(schedules)
            self.scheduler.enable()
        if not init :
            self.config['mode'] = mode
            logging.info("Mode set to {}", mode)
            self.save_config()

    def set_color(self, rgb) :
        self.np.fill(rgb)
        self.np.write()
        logging.info("Color set to {}".format(rgb))

    def set_colorspec(self, color_spec) :
        self.lamp.set_color_spec(color_spec)
        logging.info("Colorspec set to {}".format(color_spec))

    def set_color_name(self, color_name) :
        self.config['neolamp']['color_name'] = color_name
        color_spec = neolamp.COLOR_SPECS[color_name]
        self.lamp.set_color_spec(color_spec)
        logging.info("Color set to {}".format(color_name))
        self.save_config()

    def set_schedules(self, schedules) :
        self.config['scheduler']['schedules'] = schedules
        self.scheduler.set_schedules(schedules)
        logging.info("Schedules set to {}", schedules)
        self.save_config()
    
    def save_config(self) :
        core.util.save_json(self.path, self.config)
        logging.info("Configuration saved to {}".format(self.path))
                    
    def reboot(self, delay_ms=1342) :
        loop = uasyncio.get_event_loop()
        logging.info("Going down for reboot in {}ms ...".format(delay_ms))
        loop.call_later_ms(delay_ms, core.util.reboot)
    
    def reset(self) :
        if core.util.exists(self.path) :
            os.remove(self.path)
        logging.info("Neolamp reset to default settings.")
        self.reboot()
            
    def clear(self, num_calls=5) :
        for i in range(num_calls) :
            self.lamp.clear_pixels()

    def pixel_dance(self, count=10):
        for i in range(count):
            for j in range(self.np.n):
                self.lamp.set_pixel(j, Controller.random_pixel(), Controller.random_pixel(), Controller.random_pixel())

    @staticmethod
    def create_neopixel(pin, num_pixels) :
        return neopixel.NeoPixel(machine.Pin(pin), num_pixels)

    @staticmethod
    def random_pixel():
        return core.util.random_int(ub=64)
