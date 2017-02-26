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

import sys
import utime

class Log :
    '''
    This object encapsulates common logging operations
    '''
    
    DEBUG       = 'debug'
    INFO        = 'info'
    WARNING     = 'warning'
    ERROR       = 'error'
    
    def __init__(self, config, name = "unknown") :
        '''Constructor'''
        self._sinks = self.load_sinks(config)
        self._levels = config['levels']
        self._name = config['name']
        
    def debug(self, format_str, args = ()) :
        '''Send a debug log message'''
        self.log(self.DEBUG, format_str, args)

    def info(self, format_str, args = ()) :
        '''Send an info log message'''
        self.log(self.INFO, format_str, args)

    def warning(self, format_str, args = ()) :
        '''Send a warning log message'''
        self.log(self.WARNING, format_str, args)

    def error(self, format_str, args = ()) :
        '''Send an error log message'''
        self.log(self.ERROR, format_str, args)
    
    ##
    ## internal operations
    ##
    
    def load_sinks(self, config) :
        if 'sinks' in config :
            ret = {}
            sink_configs = config['sinks']
            for name, config in sink_configs.items() :
                try :
                    sink_name = name + "_sink"
                    mod = __import__(sink_name)
                    ret[name] = mod.Sink(config)
                    print("loaded sink {}".format(name))
                except Exception as e :
                    print("Error: failed to load sink {} with config {}.  Error: {}".format(name, config, e))
                    sys.print_exception(e)
            return ret
        else :
            return {}
            
    def create(self, level, format_str, args) :
        return {
            'name': self._name,
            'datetime': self.datetimestr(),
            'level': level,
            'message': format_str % args
        }
    
    def log(self, level, format_str, args = ()) :
        if level in self._levels :
            message = self.create(level, format_str, args)
            for name, sink in self._sinks.items() :
                self.do_log(sink, message)
    
    def do_log(self, sink, message) :
        try :
            sink.log(message)
        except Exception as e :
            sys.print_exception(e)

    def datetimestr(self) :
        import sys
        if sys.platform == 'esp8266':
            year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
            return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)
        else:
            return utime.strftime("%Y-%m-%dT%H:%M:%S.0000")



def module_to_dict(mod) :
    ret = {}
    for i in dir(mod) :
        if not i.startswith('__') :
            ret[i] = getattr(mod, i)
    return ret

def merge_dict(a, b) :
    ret = a.copy()
    ret.update(b)
    return ret

def get_config() :
    defaults = {
        'name': "esp8266",
        'levels': [Log.INFO, Log.WARNING, Log.ERROR],
        'sinks': {'console': None}
    }
    try :
        import log_config
        return merge_dict(
            defaults, module_to_dict(log_config)
        )
    except Exception as e :
        return defaults

logger = Log(get_config())

def debug(format_str, args = ()) :
    '''Send a debug log message'''
    logger.debug(format_str, args)

def info(format_str, args = ()) :
    '''Send an info log message'''
    logger.info(format_str, args)

def warning(format_str, args = ()) :
    '''Send a warning log message'''
    logger.warning(format_str, args)

def error(format_str, args = ()) :
    '''Send an error log message'''
    logger.error(format_str, args)

def test(ub=10) :
    for i in range(0, ub):
        logger.debug("%s %s", ('debug', 'world'))
        logger.info("%s %s", ('info', 'world'))
        logger.warning("%s %s", ('warning', 'world'))
        logger.error("%s %s", ('error', 'world'))
