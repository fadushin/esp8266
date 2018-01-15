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

import http.client
import time
import datetime
import json
import random

class Client:

    def __init__(self, host, port=80):
        self.connection = None
        self.host = host
        self.port = int(port)

    def get(self, context='/', headers={}, body=None):
        return self.request("GET", context, headers=headers)

    def put(self, context='/', headers={}, body=None):
        return self.request("PUT", context, body=body, headers=headers)

    def post(self, context='/', headers={}, body=None):
        return self.request("POST", context, body=body, headers=headers)

    def delete(self, context='/', headers={}, body=None):
        return self.request("DELETE", context, body=body, headers=headers)

    def request(self, verb, context, body=None, headers={}):
        connection = http.client.HTTPConnection(self.host, self.port)
        try:
            connection.request(verb, '/api/neolamp/' + context, body=body, headers=headers)
            response = connection.getresponse()
            body = response.read()
            ret = {
                'status': response.status,
                'headers': response.getheaders(),
                'body': body
            }
            return ret
        finally:
            connection.close()


class Action :
    
    def __init__(self) :
        pass
    
    def run(self) :
        pass

class Menu(Action) :
    
    def __init__(self, client, menu_items, prompt='neolamp> ', is_top=False) :
        self.client = client
        self.menu_items = menu_items
        self.menu_items.update({'q': ("Quit", Menu.quit)})
        self._prompt = prompt
        self.is_top = is_top
    
    @staticmethod
    def prompt(prmt) :
        import sys
        sys.stdout.write(prmt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        return line[:len(line) - 1]

    def print_menu(self) :
        print("------------")
        for (key, (desc, handler)) in self.menu_items.items() :
            print("    [{}] -- {}".format(key, desc))
        if not self.is_top :
            print("    [u] -- Return to previous menu")
        print("------------")

    @staticmethod
    def quit(_client) :
        print('goodbye')
        import sys
        sys.exit(0)

    def run(self) :
        while True :
            self.print_menu()
            response = Menu.prompt(self._prompt)
            if response and response in self.menu_items:
                try :
                    (desc, handler) = self.menu_items[response]
                    handler(self.client)
                except Exception as e :
                    print('frack! {}'.format(e))
                    import traceback
                    traceback.print_exc()
            elif response == 'u' :
                return


class TopMenu(Menu) :
    
    def __init__(self, client) :
        menu_items = {
            'n': ("Manage Neopixel", NPMenu.start),
            'c': ("Manage Colors", ColorMenu.start),
            'l': ("Manage Lamp", LampMenu.start),
            's': ("Manage Scheduler", SchedulerMenu.start),
            'm': ("Manage Mode", ModeMenu.start),
            'd': ("Manage Device", DeviceMenu.start)
        }
        Menu.__init__(self, client=client, menu_items=menu_items, is_top=True)



class NPMenu(Menu) :
    
    @staticmethod
    def start(client) :
        NPMenu(client).run()

    def __init__(self, client) :
        menu_items = {
            'l': ("List neopixel properties", NPMenu.list),
            'p': ("Set neopixel pin", NPMenu.set_pin),
            'n': ("Set num_pixels", NPMenu.set_num_pixels)
        }
        Menu.__init__(self, client=client, menu_items=menu_items)
    
    @staticmethod
    def list(client) :
        print("pin: {}".format(client.get("config/pin")['body'].decode('UTF-8')))
        print("num_pixels: {}".format(client.get("config/num_pixels")['body'].decode('UTF-8')))

    @staticmethod
    def set_pin(client) :
        response = Menu.prompt("Enter pin: ")
        client.post("np?pin={}".format(int(response)))

    @staticmethod
    def set_num_pixels(client) :
        response = Menu.prompt("Enter num_pixels: ")
        client.post("np?num_pixels={}".format(int(response)))


class ModeMenu(Menu) :
    
    @staticmethod
    def start(client) :
        ModeMenu(client).run()

    def __init__(self, client) :
        menu_items = {
            'g': ("Get mode", ModeMenu.get_mode),
            's': ("Set mode", ModeMenu.set_mode)
        }
        Menu.__init__(self, client=client, menu_items=menu_items)
    
    @staticmethod
    def get_mode(client) :
        print("mode: {}".format(client.get("config/mode")['body'].decode('UTF-8')))

    @staticmethod
    def set_mode(client) :
        response = Menu.prompt("Enter mode [off|lamp|scheduler]: ")
        if response not in ['off', 'lamp', 'scheduler'] :
            print("Mode must be one of [off|lamp|scheduler]")
        else :
            client.post("mode?mode={}".format(response))


class ColorMenu(Menu) :
    
    @staticmethod
    def start(client) :
        ColorMenu(client).run()

    def __init__(self, client) :
        menu_items = {
            'l': ("List colors", ColorMenu.list_colors),
            'g': ("Get color", ColorMenu.get_color),
            's': ("Set color", ColorMenu.set_color),
            'd': ("Delete color", ColorMenu.delete_color)
        }
        Menu.__init__(self, client=client, menu_items=menu_items)
    
    @staticmethod
    def list_colors(client) :
        print("colors: {}".format(client.get("config/color_specs")['body'].decode('UTF-8')))

    @staticmethod
    def get_color(client) :
        color_specs = client.get("config/color_specs")['body'].decode('UTF-8')
        name = Menu.prompt("Enter color {}: ".format(color_specs))
        if name not in color_specs :
            print("Color must be one of {}".format(color_specs))
        else :
            colorspec = json.loads(client.get("config/color_specs/{}?all=true".format(name))['body'].decode('UTF-8'))
            print("RED     magnitude: {:3d}   period: {:3d}   amplitude: {:3d}".format(colorspec['r']['m'], colorspec['r']['p'], colorspec['r']['a']))
            print("BLUE    magnitude: {:3d}   period: {:3d}   amplitude: {:3d}".format(colorspec['g']['m'], colorspec['g']['p'], colorspec['g']['a']))
            print("GREEN   magnitude: {:3d}   period: {:3d}   amplitude: {:3d}".format(colorspec['b']['m'], colorspec['b']['p'], colorspec['b']['a']))

    @staticmethod
    def set_color(client) :
        Menu.prompt("Enter RED magnitude period amplitude (separated by whitespace): ")
        pass

    @staticmethod
    def delete_color(client) :
        pass

class LampMenu(Menu) :
    
    @staticmethod
    def start(client) :
        LampMenu(client).run()

    def __init__(self, client) :
        menu_items = {
            'g': ("Get colorspec", LampMenu.get_colorspec),
            's': ("Set colorspec", LampMenu.set_colorspec)
        }
        Menu.__init__(self, client=client, menu_items=menu_items)
    
    @staticmethod
    def get_colorspec(client) :
        print("colorspec: {}".format(client.get("config/lamp/color_name")['body'].decode('UTF-8')))

    @staticmethod
    def set_colorspec(client) :
        color_specs = client.get("config/color_specs")['body'].decode('UTF-8')
        response = Menu.prompt("Enter colorspec {}: ".format(color_specs))
        if response not in color_specs :
            print("Mode must be one of {}".format(color_specs))
        else :
            client.post("lamp?color_name={}".format(response))

class SchedulerMenu(Menu) :
    
    @staticmethod
    def start(client) :
        SchedulerMenu(client).run()

    def __init__(self, client) :
        menu_items = {
        }
        Menu.__init__(self, client=client, menu_items=menu_items)


class DeviceMenu(Menu) :
    
    @staticmethod
    def start(client) :
        DeviceMenu(client).run()

    def __init__(self, client) :
        menu_items = {
            's': ("Get stats", DeviceMenu.get_stats),
            'r': ("Reboot", DeviceMenu.reboot),
            't': ("Reset", DeviceMenu.reset)
        }
        Menu.__init__(self, client=client, menu_items=menu_items)


    @staticmethod
    def get_stats(client) :
        stats = json.loads(client.get("stats")['body'].decode('UTF-8'))
        gcd = stats['gcd']
        print("~~~")
        print(DeviceMenu.get_basic_stats("GC", gcd))
        print(DeviceMenu.get_basic_stats("NTP", stats['ntpd']))
        print(DeviceMenu.get_basic_stats("Lamp", stats['lamp']))
        print(DeviceMenu.get_basic_stats("Scheduler", stats['scheduler']))
        print("~~~")
        print("GC stats: max: {} min: {} avg: {}".format(gcd['max_collected'], gcd['min_collected'], int(gcd['sum_collected']/gcd['num_collections'])))
        mem_alloc = gcd['mem_alloc']
        mem_free = gcd['mem_free']
        capacity = mem_alloc + mem_free
        print("Memory: allocated: {} bytes free: {} bytes ({}%)".format(mem_alloc, mem_free, int(((capacity - mem_free) / capacity) * 100.0)))
        (days, hours, minutes, seconds, millis) = DeviceMenu.get_duration(stats['uptime_ms'])
        print("Uptime: {}d {}h {}m {}.{}s".format(days, hours, minutes, seconds, millis))
        print("~~~")
        
    @staticmethod
    def get_basic_stats(moniker, stats) :
        return "{} task (calls failures avg_ms/call): {} {} {}".format(
            moniker,
            stats['num_calls'], 
            stats['num_failures'], 
            int((stats['ticks_us']/stats['num_calls'])/1000)
        )
    
    @staticmethod
    def get_duration(millis) :
        s0, ms = divmod(millis, 1000)
        m0, s = divmod(s0, 60)
        h0, m = divmod(m0, 60)
        d,  h = divmod(h0, 24)
        return (d, h, m, s, ms)
        
    @staticmethod
    def reboot(client) :
        client.post("reboot")

    @staticmethod
    def reset(client) :
        response = Menu.prompt("Are you sure you want to reset? (Any changes will be lost) [y|n]: ")
        if response not in ['y', 'n'] :
            print("Answer must be one of [y|n]")
        elif response is 'y' :
            client.post("reset")






def cli(host, port) :
    client = Client(host, port)
    menu = TopMenu(client)
    menu.run()



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "--host",
        dest="host",
        help="ESP host (192.168.4.1)",
        type="string",
        default="192.168.4.1"
    )
    parser.add_option(
        "--port",
        dest="port",
        help="ESP port (80)",
        type="int",
        default=80
    )
    (options, args) = parser.parse_args()
    cli(options.host, port=options.port)
