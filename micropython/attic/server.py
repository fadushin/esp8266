#!/usr/bin/env python
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
import sys
import log
from thread import *

def connection_thread(connection, address) :
    while True :
        data = connection.recv(4096)
        if not data: 
            break
        print "%s:%d: %s" % (address[0], address[1], data)
        reply = 'ok'
        connection.sendall(reply)
    connection.close()

class Server :
    
    def __init__(self, config = {'host': '0.0.0.0', 'port': 44403}) :
        self._host = config['host']
        self._port = config['port']
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._state = 'stopped'
        #self._logger = log.Log()

    def start(self) :
        self._socket.bind((self._host, self._port))
        print("bound to %s:%d.  Listening..." % (self._host, self._port))
        self._listen()
    
    def _listen(self) :
        self._state = 'running'
        self._socket.listen(10)
        while True :
            if self._state != 'running' :
                break
            else :
                connection, address = self._socket.accept()
                start_new_thread(connection_thread, (connection, address))
    
 
server = Server()
server.start()
 