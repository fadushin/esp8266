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
import uasyncio

import uhttpd
import uhttpd.api_handler
#import uhttpd.file_handler

import neolamp.api
import neolamp.controller



controller_ = None

def run():
    ##
    ## Start the controller and signal we are starting
    ##
    global controller_
    controller_ = neolamp.controller.Controller()
    controller_.pixel_dance()
    controller_.clear()
    ##
    ## Set up and start the web server
    ##
    #import system.api
    api_handler = uhttpd.api_handler.Handler([
        (['neolamp'], neolamp.api.Handler(controller_))
        #, (['system'], system.api.Handler())
    ])
   # file_handler = uhttpd.file_handler.Handler('/www/neolamp')
    server = uhttpd.Server([
        ('/api', api_handler)
        #,('/', file_handler)
    ], {'max_headers': 50, 'backlog': 10})
    server.run()


def resume() :
    uasyncio.get_event_loop().run_forever()




