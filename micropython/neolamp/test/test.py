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


def test(host, port=80, pin=2, num_pixels=1) :
    client = Client(host, port)
    try :
        reset(client, pin, num_pixels)
        test_lamp_colors(client)
        test_schedule(client)
        # test_colorspec(client)
    finally :
        reset(client, pin, num_pixels)


def reset(client, pin=2, num_pixels=1) :
    print("Resetting ESP and setting pin to {} and num_pixels to {} ...".format(pin, num_pixels))
    client.post("reset")
    sleep_ms(10000)
    client.post("np?pin={}&num_pixels={}".format(pin, num_pixels))

def test_lamp_colors(client) :
    print("Testing lamp colors ...")
    colors = get_colors(client)
    try :
        set_mode(client, "lamp")
        for color in colors :
            test_lamp_color(client, color)
    finally :
        set_mode(client, "off")


def get_colors(client) :
    return json.loads(client.get('config/color_specs')['body'].decode('UTF-8'))

def test_schedule(client) :
    print("Testing schedule ...")
    colors = get_colors(client)
    schedule = create_schedule(colors)
    try :
        print("Setting wake_and_bake schedule to {} ...".format(schedule))
        client.post('schedule?name=wake_and_bake', headers={'content-type': 'application/json'}, body=json.dumps(schedule).encode('UTF-8'))
        set_mode(client, "scheduler")
        sleep_ms(60*1000)
    finally :
        set_mode(client, "off")


def create_schedule(colors) :
    colors.remove('black')
    colors.remove('white')
    secs = time.time()
    n = len(colors)
    return {
        'dow': [time.localtime(secs).tm_wday + 1],
        'seq': [
            {
                'time': create_time(secs),
                'color_name': 'black'
            },
            {
                'time': create_time(secs + 30),
                'color_name': colors[random.randrange(n)]
            },
            {
                'time': create_time(secs + 60),
                'color_name': 'black'
            }
        ]
    }

def create_time(secs) :
    localtime = time.localtime(secs)
    h = localtime.tm_hour
    m = localtime.tm_min
    s = localtime.tm_sec
    return {
            'h': h,
            'm': m,
            's': s
    }

def test_lamp_color(client, color) :
    print("Testing lamp color {} ...".format(color))
    client.post('lamp?color_name={}'.format(color))
    sleep_ms(5000)


def set_mode(client, mode) :
    client.post('mode?mode={}'.format(mode))


def sleep_ms(ms) :
    print("Sleeping {}ms ...".format(ms))
    time.sleep(ms/1000)

    
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
    parser.add_option(
        "--pin",
        dest="pin",
        help="ESP neopixel pin (2)",
        type="int",
        default=2
    )
    parser.add_option(
        "--num_pixels",
        dest="num_pixels",
        help="ESP neopixel num_pixels (1)",
        type="int",
        default=1
    )
    (options, args) = parser.parse_args()
    test(options.host, port=options.port, pin=options.pin, num_pixels=options.num_pixels)
