"""
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
"""
import socket
import network
import micropython
import sys
from ulog import logger

SO_REGISTER_HANDLER = const(20)
CONNECTION_TIMEOUT = const(30)


class Server:
    def __init__(self, port, handler, bind_addr='0.0.0.0',
                 timeout=CONNECTION_TIMEOUT, use_ssl=False):
        self._port = port
        self._handler = handler
        self._bind_addr = bind_addr
        self._timeout = timeout
        self._use_ssl = use_ssl
        self._server_socket = None
        self._client_socket = None

    def handle_receive(self, client_socket, remote_addr):
        try:
            done, response = self._handler.handle_request(client_socket,
                                                          remote_addr)
            if response and len(response) > 0:
                logger.debug(
                    "A non-zero response was returned from the utcp_server handler")
                client_socket.write(response)
            if done:
                logger.debug(
                    "The utcp_server handler is done.  Closing socket.")
                self.close(client_socket)
                return False
            else:
                logger.debug("The utcp_server handler is not done.")
                self._client_socket = client_socket
                return True
        except Exception as e:
            logger.error("Trapped exception '{}' on receive.".format(e))
            sys.print_exception(e)
            self.close(client_socket)
            return False

    def handle_accept(self, server_socket):
        client_socket, remote_addr = server_socket.accept()
        logger.debug("Accepted connection from: {}".format(remote_addr))
        client_socket.settimeout(self._timeout)
        if self._use_ssl:
            import ussl
            client_socket = ussl.wrap_socket(client_socket, server_side=True)
            logger.debug("Connection will use SSL")
        while self.handle_receive(client_socket, remote_addr):
            pass

    def start(self):
        micropython.alloc_emergency_exception_buf(100)
        ##
        ## Start the listening socket.  Handle accepts asynchronously
        ## in handle_accept/1
        ##
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                       1)
        self._server_socket.bind((self._bind_addr, self._port))
        self._server_socket.listen(0)
        self._server_socket.setsockopt(socket.SOL_SOCKET, SO_REGISTER_HANDLER,
                                       self.handle_accept)
        ##
        ## Report the interfaces on which we are listening
        ##
        ap = network.WLAN(network.AP_IF)
        if ap.active():
            ifconfig = ap.ifconfig()
            logger.info(
                "TCP server started on {}:{}".format(ifconfig[0], self._port))
        sta = network.WLAN(network.STA_IF)
        if sta.active():
            ifconfig = sta.ifconfig()
            logger.info(
                "TCP server started on {}:{}".format(ifconfig[0], self._port))

    def stop(self):
        if self._client_socket:
            self.client_socket.close()
        if self._server_socket:
            self._server_socket.close()

    def close(self, socket_):
        logger.debug("Closing socket {}".format(socket_))
        socket_.close()
        self._client_socket = None
