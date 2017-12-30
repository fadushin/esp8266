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

import ujson
import http.client
import core.task
import logging

class Timezoned(core.task.TaskBase) :

    def __init__(self, sleep_ms=3*60*60*1000, verbose=False) :
        core.task.TaskBase.__init__(self, sleep_ms, verbose=verbose)
        self.verbose = verbose
        self.offset_hours = 0
        self.buf = bytearray(1)
    
    def perform(self) :
        connection = http.client.HTTPConnection("timezoneapi.io")
        try :
            response = connection.request("GET", "api/ip").getresponse()
            self.offset_hours = self.find_offset_hours(response)
            logging.info("Timezoned: offset_hours: {}", self.offset_hours)
            return True
        finally :
            connection.close()
    
    def get_offset_hours(self) :
        return self.offset_hours

    def find_offset_hours(self, response) :
        while True :
            if self.find("offset_hours\"", response) :
                while self.read_byte(response) != ord('"') :
                    pass
                # we just read an opening quote
                buf = bytearray(8)
                i = 0
                b = self.read_byte(response)
                while b != ord('"') :
                    buf[i] = b
                    b = self.read_byte(response)
                    i += 1
                s = "".join(map(chr, buf[:i]))
                return int(s)
        # blob = ujson.load(response.socket)
        # return int(blob['data']['datetime']['offset_hours'])

    def read_byte(self, response) :
        num_read = response.socket.readinto(self.buf)
        if num_read == 0 :
            raise RuntimeError("offset not found in response")
        return self.buf[0]

    def find(self, s, response) :
        for c in s.encode('UTF-8') :
            if c == self.read_byte(response) :
                pass
            else :
                return False
        return True
            
