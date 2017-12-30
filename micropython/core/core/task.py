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
import sys
import core.util



class TaskBase :

    INIT=b'0'
    RUNNING=b'1'
    STOPPING=b'2'
    STOPPED=b'3'

    def __init__(self, sleep_ms, verbose=False) :
        self.sleep_ms = sleep_ms
        self._verbose = verbose
        self.state = TaskBase.INIT
        self.disabled = False
        self.num_calls = 0
        self.num_failures = 0
        self.last_retry_ms = None

    def register(self) :
        loop = uasyncio.get_event_loop()
        loop.create_task(self.loop())
        self.state = TaskBase.RUNNING
        return self

    def isRunning(self) :
        return self.state == TaskBase.RUNNING

    def cancel(self) :
        self.state = TaskBase.STOPPING
    
    def disable(self) :
        self.disabled = True
    
    def enable(self) :
        self.disabled = False

    def stats(self) :
        return {
            'num_calls': self.num_calls,
            'num_failures': self.num_failures
        }

    def perform(self) :
        pass

    async def loop(self) :
        if self._verbose :
            logging.info("TaskBase: loop starting.")
        while self.isRunning() :
            if not self.disabled :
                try :
                    self.num_calls += 1
                    result = self.perform()
                    if not result:
                        return
                    self.last_retry_ms = None
                except Exception as e :
                    if not self.last_retry_ms :
                        self.last_retry_ms = 500
                    else :
                        self.last_retry_ms = min(self.sleep_ms, self.last_retry_ms * 2)
                    self.num_failures += 1
                    logging.info("An error occurred performing {}: {}".format(self, e))
                    sys.print_exception(e)
                await uasyncio.sleep_ms(self.sleep_ms if not self.last_retry_ms else self.last_retry_ms)
            else :
                await uasyncio.sleep_ms(914)
        self.state = TaskBase.STOPPED
        if self._verbose :
            logging.info("TaskBase: loop terminated.")
        return


class Gcd(TaskBase) :

    def __init__(self, sleep_ms=5*1000, verbose=False) :
        TaskBase.__init__(self, sleep_ms)
        self.verbose = verbose
        self.mem_free = 0
        self.mem_alloc = 0
        self.min_collected = 2**32
        self.max_collected = 0
        self.sum_collected = 0
        self.num_collections = 0

    def stats(self) :
        return core.util.update_dict(
            TaskBase.stats(self), {
                'mem_free': self.mem_free,
                'mem_alloc': self.mem_alloc,
                'min_collected': self.min_collected,
                'max_collected': self.max_collected,
                'sum_collected': self.sum_collected,
                'num_collections': self.num_collections
            }
        )

    def perform(self) :
        import gc
        mem_free_before = gc.mem_free()
        gc.collect()
        self.mem_free = gc.mem_free()
        self.mem_alloc = gc.mem_alloc()
        mem_collected = self.mem_free - mem_free_before
        if mem_collected < self.min_collected :
            self.min_collected = mem_collected
        if self.max_collected < mem_collected :
            self.max_collected = mem_collected
        self.sum_collected += mem_collected
        self.num_collections += 1
        return True


class Ntpd(TaskBase) :

    def __init__(self, sleep_ms=15*60*1000, verbose=True) :
        TaskBase.__init__(self, sleep_ms)
        self.verbose = verbose
        self.min_skew = 2**31 - 1
        self.max_skew = -self.min_skew

    def stats(self) :
        return core.util.update_dict(
            TaskBase.stats(self), {
                'min_skew': self.min_skew,
                'max_skew': self.max_skew
            }
        )

    def perform(self) :
        import ntptime
        import core.util
        import utime
        old_secs = utime.time()
        ntptime.settime()
        new_secs = utime.time()
        skew = new_secs - old_secs
        self.min_skew = min(skew, self.min_skew)
        self.max_skew = max(skew, self.max_skew)
        if self.verbose :
            logging.info("ntpd: time set to {} UTC (skew: {} secs)".format(core.util.secs_to_string(new_secs), skew))
        return True
