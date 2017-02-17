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
import time
import socket
import sys
from ulog import logger
import gc

VERSION = "master"


class NotFoundException(Exception):
    pass


class BadRequestException(Exception):
    pass


class ForbiddenException(Exception):
    pass


def get_relative_path(http_request):
    path = http_request['path']
    prefix = http_request['prefix']
    return path[len(prefix):]


class Server:
    def __init__(self, handlers, config={}):
        self._handlers = handlers
        self._config = self.update(self.default_config(), config)
        self._tcp_server = TCPServer(
            bind_addr=self._config['bind_addr'],
            port=self._config['port'],
            timeout=self._config['timeout'],
            handler=self,
            backlog=self._config['backlog']
        )
        self.reset_reqbuf()

    #
    # API
    #

    def run(self):
        logger.info("uhttpd-{} starting...".format(VERSION))
        try:
            self._tcp_server.run()
        finally:
            logger.info("uhttpd-{} stopped.".format(VERSION))

    #
    # Callbacks
    #

    def reset_reqbuf(self):
        self._reqbuf = [b'']
        self._reqlen = 0

    def handle_request(self, client_socket, tcp_request):
        rlen = self._config['max_header_length'] - self._reqlen
        if rlen <= 0:
            raise Exception("Maximum header length exceeded")
        recv = client_socket.recv(self._config['max_header_length'] - self._reqlen)
        self._reqlen += len(recv)
        recv = self._reqbuf.pop() + recv
        while b'\r\n' in recv:
            line, recv = recv.split(b'\r\n',1)
            self._reqbuf.append(line)
            if not line:
                self._reqbuf.append(recv)
                self._reqbuf.reverse()
                try:
                    return self.process_request(self._reqbuf, client_socket, tcp_request)
                finally:
                    self.reset_reqbuf();
            elif len(self._reqbuf) > self._config['max_headers']:
                raise Exception("Maximum header count exceeded")
        self._reqbuf.append(recv)
        return (True, None)

    def process_request(self, reqbuf, client_socket, tcp_request):
        http_request = {
            'tcp': tcp_request
        }
        try:
            gc.collect()
            #
            # parse out the heading line, to get the verb, path, and protocol
            #
            heading = self.parse_heading(
                self.readline(reqbuf).decode('UTF-8'))
            logger.debug("Parsed heading {}".format(heading))
            http_request.update(heading)
            #
            # find the handler for the specified path.  If we don't have
            # one registered, we raise a NotFoundException, but only after
            # reading the payload.
            #
            path = http_request['path']
            handler = None
            for prefix, h in self._handlers:
                if path.startswith(prefix):
                    http_request['prefix'] = prefix
                    handler = h
                    logger.debug("Found handler for prefix {}".format(prefix))
                    break
            #
            # Parse out the headers
            #
            headers = {}
            while True:
                line = self.readline(reqbuf)
                if not line or line == b'\r\n':
                    break
                k, v = Server.parse_header(line.decode('UTF-8'))
                headers[k.lower()] = v
            #logger.debug("Parsed headers {}".format(headers))
            http_request['headers'] = headers
            #
            # If the headers have a content length, then read the body
            #
            content_length = 0
            if 'content-length' in headers:
                content_length = int(headers['content-length'])
                logger.debug("content_length: {}".format(content_length))
                if content_length > self._config['max_content_length']:
                    raise BadRequestException("Content size exceeds maximum allowable")
                elif content_length > 0:
                    body = self.readline(reqbuf)
                    if len(body) < content_length:
                        body += client_socket.read(content_length-len(body))
                    elif len(body) > content_length:
                        reqbuf.append(body[content_length:])
                        body = body[:content_length]
                    logger.debug("Read body: {}".format(body))
            #
            # If there is no handler, then raise a NotFound exception
            #
            if not handler:
                raise NotFoundException("No Handler for path {}".format(path))

            #
            # Authenticate the user, if configured to do so.  If required
            # and there is no authorization header, reply with a 401 and
            # specify the basic auth realm.  Otherwise, try to validate the
            # supplied credentials.  Audit either case.
            #
            if self._config['require_auth']:
                if not 'authorization' in headers:
                    return self.unauthorized_error(client_socket)
                else:
                    remote_addr = tcp_request['remote_addr']
                    is_authorized, user = self.is_authorized(headers['authorization'])
                    if not is_authorized:
                        logger.info("UNAUTHORIZED {}".format(remote_addr))
                        return self.unauthorized_error(client_socket)
                    else:
                        logger.info("AUTHORIZED {}".format(remote_addr))
                        http_request['user'] = user
            #
            # get the response from the active handler and serialize it
            # to the socket
            #
            response = handler.handle_request(http_request)
            return Server.response(response)
        except BadRequestException as e:
            return Server.bad_request_error(e)
        except ForbiddenException as e:
            return Server.forbidden_error(e)
        except NotFoundException as e:
            return Server.not_found_error(e)
        except BaseException as e:
            return Server.internal_server_error(e)
        finally:
            gc.collect()

    #
    # Internal operations
    #

    @staticmethod
    def update(a, b):
        a.update(b)
        return a

    @staticmethod
    def default_config():
        return {
            'bind_addr': '0.0.0.0',
            'port': 80,
            'timeout': 30,
            'require_auth': False,
            'realm': "esp8266",
            'user': "admin",
            'password': "uhttpD",
            'max_headers': 25,
            'max_content_length': 1024,
            'max_header_length': 1024,
            'backlog': 5
        }

    def readline(self, reqbuf):
        return reqbuf.pop()

    @staticmethod
    def parse_heading(line):
        ra = line.split()
        try:
            return {
                'verb': ra[0].lower(),
                'path': ra[1],
                'protocol': ra[2]
            }
        except:
            raise BadRequestException()

    @staticmethod
    def parse_header(line):
        ra = line.split(":")
        return (ra[0].strip(), ra[1].strip())

    def is_authorized(self, authorization):
        import ubinascii
        try:
            tmp = authorization.split()
            if tmp[0].lower() == "basic":
                str = ubinascii.a2b_base64(tmp[1].strip().encode()).decode()
                ra = str.split(':')
                auth_result = ra[0] == self._config['user'] and ra[1] == self._config['password']
                return auth_result, ra[0]
            else:
                raise BadRequestException(
                    "Unsupported authorization method: {}".format(tmp[0]))
        except Exception as e:
            raise BadRequestException(e)

    @staticmethod
    def server_name():
        return "uhttpd/{} (running in your devices)".format(VERSION)

    @staticmethod
    def format_heading(code):
        return "HTTP/1.0 {} {}".format(code, Server.lookup_code(code))

    @staticmethod
    def lookup_code(code):
        if code == 200:
            return "OK"
        elif code == 400:
            return "Bad Request"
        elif code == 401:
            return "Unauthorized"
        elif code == 403:
            return "Forbidden"
        elif code == 404:
            return "Not Found"
        elif code == 500:
            return "Internal Server Error"
        else:
            return "Unknown"

    @staticmethod
    def format_headers(headers):
        ret = ""
        for k, v in headers.items():
            ret += "{}: {}\r\n".format(k, v)
        return ret

    @staticmethod
    def response(response):
        return (False, Server.serialize(response))

    @staticmethod
    def serialize(response):
        #
        # write the heading and headers
        #
        headers = "{}\r\n{}\r\n".format(
            Server.format_heading(response['code']),
            Server.format_headers(Server.update(
                response['headers'], {'Server': Server.server_name()}
            ))
        ).encode('UTF-8')
        #
        # Write the body, if it's present
        #
        return (headers, response.get('body'))

    def unauthorized_error(self, client_socket):
        headers = {
            'www-authenticate': "Basic realm={}".format(self._config['realm'])
        }
        return Server.error(client_socket, 401, "Unauthorized", None, headers)

    @staticmethod
    def bad_request_error(e):
        error_message = "Bad Request {}:".format(e)
        return Server.error(400, error_message, e)

    @staticmethod
    def forbidden_error(e):
        error_message = "Forbidden {}:".format(e)
        return Server.error(403, error_message, e)

    @staticmethod
    def not_found_error(e):
        error_message = "Not Found: {}".format(e)
        return Server.error(404, error_message, e)

    @staticmethod
    def internal_server_error(e):
        sys.print_exception(e)
        error_message = "Internal Server Error: {}".format(e)
        return Server.error(500, error_message, e)

    @staticmethod
    def error(code, error_message, e, headers={}):
        logger.debug("Error!  code: {} error_message: {} exception: {}".format(code, error_message, e))
        ef = lambda stream: Server.stream_error(stream, error_message, e)
        response = Server.generate_error_response(code, ef, headers)
        return Server.response(response)

    @staticmethod
    def stream_error(stream, error_message, e):
        stream.write(error_message)
        if e:
            stream.write('<pre>')
            stream.write(Server.stacktrace(e))
            stream.write('</pre>')

    @staticmethod
    def stacktrace(e):
        import uio
        buf = uio.BytesIO()
        sys.print_exception(e, buf)
        return buf.getvalue()

    @staticmethod
    def generate_error_response(code, ef, headers={}):
        data1 = '<html><body><header>uhttpd/{}<hr></header>'.format(
            VERSION).encode('UTF-8')
        # message data in ef will go here
        data2 = '</body></html>'.encode('UTF-8')
        body = lambda stream: Server.write_html(stream, data1, ef, data2)
        return {
            'code': code,
            'headers': Server.update({
                'content-type': "text/html",
            }, headers),
            'body': body
        }

    @staticmethod
    def write_html(stream, data1, ef, data2):
        stream.write(data1)
        ef(stream)
        stream.write(data2)

import uselect

class TCPServer:
    def __init__(self, port, handler, bind_addr='0.0.0.0',
                 timeout=30, backlog=5):
        self._port = port
        self._handler = handler
        self._bind_addr = bind_addr
        self._timeout = timeout
        self._backlog = backlog
        self._poller = uselect.poll()
        self.initialize()

    def initialize(self):
        self._server_socket = None
        self._client_socket = None
        self._client_map = {}
        gc.collect()

    def handle_client(self):
        try:
            state, response = self._handler.handle_request(self._client_socket, { 'remote_addr': self._client_addr })
            gc.collect()
            if response is not None:
                self._client_socket.write(response[0])
                if response[1] is not None:
                    response[1](self._client_socket)
            return state
        except Exception as e:
            sys.print_exception(e)
        finally:
            gc.collect()

    def handle_accept(self, client):
        client_socket, client_addr = client
        logger.info("+ {}".format(client_addr))
        client_socket.settimeout(self._timeout)
        self._poller.register(client_socket, uselect.POLLIN)
        self._client_map[client_addr] = (client_socket,time.time())

    def handle_close(self, client_socket, client_addr=None):
        if client_addr is None:
            for key in self._client_map:
                if self._client_map[key][0] == client_socket:
                    client_addr = key
                    break
        logger.info("- {}".format(client_addr))
        del self._client_map[client_addr]
        self._poller.unregister(client_socket)
        client_socket.close()

    def run(self):
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self._bind_addr, self._port))
            self._server_socket.listen(self._backlog)
            self._poller.register(self._server_socket, uselect.POLLIN)
            logger.debug("Listening on {}:{} with backlog {}".format(self._bind_addr, self._port, self._backlog))
            while True:
                ready = self._poller.poll(1000)
                for entry in ready:
                    if entry[0] == self._server_socket:
                        self.handle_accept(self._server_socket.accept())
                    else:
                        if self._client_socket is None:
                            self._client_socket = entry[0]
                            for key in self._client_map:
                                if self._client_map[key][0] == entry[0]:
                                    self._client_addr = key
                                    break
                        elif entry[0] != self._client_socket:
                            # Sorry we are serving another guy, please hold on...
                            continue
                        if not self.handle_client():
                            self.handle_close(self._client_socket)
                            self._handler.reset_reqbuf()
                            self._client_socket = None
                            gc.collect()
                        break

                if len(ready) == 0:
                    now = time.time()
                    for client_addr, client_info in self._client_map.items():
                        if now - client_info[1] > self._timeout:
                            self.handle_close(client_info[0], client_addr)
                            if client_info[0] == client_info[0]:
                                self._handler.reset_reqbuf()
                                self._client_socket = None
                    gc.collect()
        finally:
            for client_addr, client_info in self._client_map.items():
                logger.info("* {}".format(client_addr))
                self._poller.unregister(client_info[0])
                client_info[0].close()
            if self._server_socket:
                self._poller.unregister(self._server_socket)
                self._server_socket.close()
            # free up resources
            self.initialize()
