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
import time
from log import logger
import util

class WeatherStation :
    '''WeatherStation object
    
    This object represents a weatherunderground.com weather station,
    as defined by a weatherundergroud.com stationid and password, which
    is supplied through this object's constructor.
    
    When the run operation is called, the will take a measurement from
    a DHT sensor and send the results to the configured weatherunderground.com 
    station.  It will sleep for a spefified number of seconds and repeat
    the process, until the application is terminated (e.g., via ^C)
    '''

    def __init__(self, stationid, password) :
        '''Constructor
        
        stationid   -- The weatherunderground.com station id
        password    -- The password associated with the specified station id
        '''
        self._stationid = stationid
        self._password = password
    
    def run(self, pin=2, sleep_s=30) :
        '''Run the weather station
        
        Take a DHT measurement from the specified pin and upload the results every
        sleep_s seconds.  This function runs indefinitely.
        
        pin             -- the GPIO pin from which to read DHT11 sensor data (default: 2)
        sleep_s         -- the number of seconds to sleep between measurements (default: 30)
        '''
        while True :
            self.tick(pin)
            logger.debug("Sleeping %s secs ..." % sleep_s)
            time.sleep(sleep_s)
    
    def tick(self, pin=2) :
        import dht
        import machine
        try :
            d = dht.DHT11(machine.Pin(pin))
            d.measure()
            tempf = 32.0 + 1.8 * d.temperature()
            humidity = d.humidity()
            logger.debug("Read measurements off DHT11: temp(f): %s humidity: %s" % (tempf, humidity))
            self._upload(tempf, humidity)
            util.clear_led_error()
        except Exception as E :
            logger.error("An error occurred taking measurements: %s", E)
            util.set_led_error()
    
    ##
    ## Internal operations
    ##

    def _upload(self, tempf, humidity) :
        import socket
        addr_info = socket.getaddrinfo("weatherstation.wunderground.com", 80)
        url = "/weatherstation/updateweatherstation.php?ID=%s&PASSWORD=%s&dateutc=now&tempf=%s&humidity=%s&softwaretype=ESP8266+DHT11&action=updateraw" % (self._stationid, self._password, tempf, humidity)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.connect(addr)
        request = b"GET %s HTTP/1.0\r\nHost: weatherstation.wunderground.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n" % url
        logger.debug("Request: %s" % request)
        val = s.send(request)
        logger.debug("val: %s" % val)
        logger.debug("Response: %s" % s.read())
        s.close()
        logger.info("Uploaded tempf: %s humidity: %s to wunderground.com stationid %s", (tempf, humidity, self._stationid))

try :
    import ws_config
    station = WeatherStation(ws_config.stationid, ws_config.password)
except Exception as E :
    logger.error("An error occurred creating a weather station: %s" % E)
