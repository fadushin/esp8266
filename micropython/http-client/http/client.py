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

import usocket as socket
import logging

HTTP_PORT=80
HTTPS_PORT=443

class HTTPConnection :

    def __init__(self, host, port=HTTP_PORT):
        self.host = host
        self.port = int(port)
        addr_info = socket.getaddrinfo(host, port)
        self.addr = addr_info[0][-1]
        self.connected = False
        self.socket = socket.socket()
    
    def connect(self) :
        if not self.connected :
            self.socket.connect(self.addr)
            self.connected = True
    
    def close(self) :
        if self.connected :
            self.socket.close()

    def putrequest(self, method, url) :
        self.socket.write(method)
        self.socket.write(b' /')
        self.socket.write(url)
        self.socket.write(b' HTTP/1.0\r\nHost: ')
        self.socket.write(self.host)
        self.socket.write(b'\r\n')
    
    def putheader(self, k, v) :
        self.socket.write(k)
        self.socket.write(b': ')
        self.socket.write(v)
        self.socket.write(b'\r\n')

    def endheader(self) :
        self.socket.write(b'\r\n')
        
    def send(self, data) :
        self.socket.write(data)

    def request(self, method, url, data=None, headers={}) :
        try :
            self.connect()
            self.putrequest(method, url)
            for (k, v) in headers.items() :
                self.putheader(k, v)
            if data :
                self.putheader(b'Content-Length', str(len(data)))
                self.endheader()
                self.send(data)
            else :
                self.endheader()
            return self
        except Exception :
            self.close()
            raise
    
    def getresponse(self) :
        return HTTPResponse(self.socket, self)


class HTTPResponse :

    def __init__(self, socket, owner) :
        self.socket = socket
        self.owner = owner
        try :
            line = readline(self.socket)
            (version, status, _rest) = line.split(None, 2)
            self.version = version
            self.status = int(status)
            self.headers = {}
            while True:
                line = readline(self.socket)
                if not line or line == '\r\n' :
                    break
                else :
                    (h, v) = HTTPResponse._parse_header(line)
                    self.headers[h] = v
        except Exception as e :
            logging.info("Error reading response: {}", e)
            self.owner.close()
            raise
            
    def read(self) :
        return self.socket.read()

    @staticmethod
    def _parse_header(line):
        ra = line.split(":")
        return (ra[0].strip(), ra[1].strip())


def readline(socket) :
    return socket.readline().decode('UTF-8')