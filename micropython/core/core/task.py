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
import logging
import logging
import sys

STATE_INIT=b'0'
STATE_RUNNING=b'1'
STATE_STOPPING=b'2'
STATE_STOPPED=b'3'


class TaskBase :

    def __init__(self, sleep_ms, verbose=False) :
        self.sleep_ms = sleep_ms
        self._verbose = verbose
        self.state = STATE_INIT
        self.disabled = False

    def register(self) :
        loop = uasyncio.get_event_loop()
        loop.create_task(self.loop())
        self.state = STATE_RUNNING
        return self

    def isRunning(self) :
        return self.state == STATE_RUNNING

    def cancel(self) :
        self.state = STATE_STOPPING
    
    def disable(self) :
        self.disabled = True
    
    def enable(self) :
        self.disabled = False

    def perform(self) :
        pass

    async def loop(self) :
        if self._verbose :
            logging.info("TaskBase: loop starting.")
        while self.isRunning() :
            if not self.disabled :
                result = None
                try :
                    result = self.perform()
                except Exception as e :
                    logging.info("An error occurred performing {}: {}".format(self, e))
                    sys.print_exception(e)
                if not result:
                    break
                else :
                    await uasyncio.sleep_ms(self.sleep_ms)
            else :
                await uasyncio.sleep_ms(914)
        self.state = STATE_STOPPED
        if self._verbose :
            logging.info("TaskBase: loop terminated.")
        return


class Gcd(TaskBase) :

    def __init__(self, sleep_ms=5*1000, verbose=False) :
        TaskBase.__init__(self, sleep_ms)
        self.verbose = verbose

    def perform(self) :
        import gc
        gc.collect()
        return True


class Ntpd(TaskBase) :

    def __init__(self, sleep_ms=15*60*1000, verbose=True) :
        TaskBase.__init__(self, sleep_ms)
        self.verbose = verbose

    def perform(self) :
        import ntptime
        import core.util
        import utime
        old_secs = utime.time()
        try :
            ntptime.settime()
            new_secs = utime.time()
            if self.verbose :
                logging.info("ntpd: time set to {} UTC (skew: {} secs)".format(core.util.secs_to_string(new_secs), new_secs - old_secs))
        except BaseException as e :
            logging.info("ntpd: caught excption setting time: {}".format(e))
        return True
