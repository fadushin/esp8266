'''
Copyright (c) dushin.net  All Rights Reserved

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of dushin.net nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import socket
import util

class Log :
    '''
    This object encapsulates common logging operations
    '''
    
    DEBUG       = 'debug'
    INFO        = 'info'
    WARNING     = 'warning'
    ERROR       = 'error'
    
    def __init__(self, debug=False) :
        '''Constructor'''
        config = self._get_config()
        self._host = config['host']
        self._port = int(config['port'])
        self._levels = config['levels']
        self._debug = debug
    
    def debug(self, format_str, args = ()) :
        '''Send a debug log message'''
        self._log(self.DEBUG, format_str, args)

    def info(self, format_str, args = ()) :
        '''Send an info log message'''
        self._log(self.INFO, format_str, args)

    def warning(self, format_str, args = ()) :
        '''Send a warning log message'''
        self._log(self.WARNING, format_str, args)

    def error(self, format_str, args = ()) :
        '''Send an error log message'''
        self._log(self.ERROR, format_str, args)
    
    ##
    ## internal operations
    ##
    
    def _get_time(self) :
        import time
        (year, month, day, hour, minute, second, millis, _tzinfo) = time.localtime()
        return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)
        
    def _format(self, level, format_str, args) :
        return "%s [%s]: " % (util.datetimestr(), level) + format_str % args
    
    def _log(self, level, format_str, args = ()) :
        if level in self._levels :
            message = self._format(level, format_str, args)
            print(message)
            if self._host :
                self._send(message)
    
    def _get_connection(self) :
        addr_info = socket.getaddrinfo(self._host, self._port)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.connect(addr)
        return s
    
    def _send(self, message) :
        try :
            connection = self._get_connection()
            connection.send(message)
            connection.close()
        except Exception as E :
            if self._debug :
                print(
                    self._format(
                        self.ERROR, "An error occurred sending a log message to %s%d: %s", (self._host, self._port, E)
                    )
                )

    def _get_config(self) :
        defaults = {
            'levels': [self.INFO, self.WARNING, self.ERROR],
            'host': None,
            'port': 0
        }
        try :
            import log_config
            return util.merge_dict(
                defaults, util.module_to_dict(log_config)
            )
        except Exception as E :
            print(self._format(self.ERROR, "Error loading log_config: %s", E))
            return defaults
        
            
logger = Log()

def test(ub=10) :
    for i in range(0, ub):
        logger.debug("%s %s", ('debug', 'world'))
        logger.info("%s %s", ('info', 'world'))
        logger.warning("%s %s", ('warning', 'world'))
        logger.error("%s %s", ('error', 'world'))
