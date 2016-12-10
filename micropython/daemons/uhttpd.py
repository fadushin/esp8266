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
import gc


class NotFoundException(Exception):
    pass


class BadRequestException(Exception):
    pass


class Server:
    def __init__(self, handlers, config={}):
        self._handlers = handlers
        self._config = self.update(self.default_config(), config)
        self._tcp_server = TCPServer(
            port=self._config['port'],
            handler=self,
            use_ssl=self._config['use_ssl'])
        self._version = "pre-0.1"

    #
    # API
    #

    def start(self):
        self._tcp_server.start()

    def stop(self):
        self._tcp_server.stop()

    #
    # Callbacks
    #

    def handle_request(self, client_socket, remote_addr):
        try:
            gc.collect()
            #
            # parse out the heading line, to get the verb, path, and protocol
            #
            request = self.parse_heading(
                self.readline(client_socket).decode('UTF-8'))
            request['remote_addr'] = remote_addr
            #
            # find the handler for the specified path.  If we don't have
            # one registered, raise a NotFoundException
            #
            path = request['path']
            handler = None
            relative_path = None
            for prefix, h in self._handlers:
                if path.startswith(prefix):
                    relative_path = path[len(prefix):]
                    handler = h
                    logger.debug(
                        "Found uhttpd handler {}".format(handler.module()))
                    break
            if not handler:
                raise NotFoundException("No Handler for path {}".format(path))
            request['relative_path'] = relative_path
            #
            # Otherwise, parse out the headers
            #
            headers = {}
            while True:
                line = self.readline(client_socket)
                if not line or line == b'\r\n':
                    break
                k, v = self.parse_header(line.decode('UTF-8'))
                headers[k.lower()] = v
            request['headers'] = headers
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
                    if not self.is_authorized(headers['authorization']):
                        logger.info("UNAUTHORIZED {}".format(request['remote_addr']))
                        return self.unauthorized_error(client_socket)
                    else:
                        logger.info("AUTHORIZED {}".format(request['remote_addr']))
            #
            # If the headers have a content length, then read the body
            #
            content_length = 0
            if 'Content-Length' in headers:
                content_length = int(headers['Content-Length'])
            if content_length > 0:
                body = client_socket.read(content_length)
                request['body'] = body
            #
            # get the response from the active handler and serialize it
            # to the socket
            #
            response = handler.handle_request(request)
            return self.response(client_socket, response)
        except BadRequestException as e:
            return self.bad_request_error(client_socket, e)
        except NotFoundException as e:
            return self.not_found_error(client_socket, e)
        except BaseException as e:
            return self.internal_server_error(client_socket, e)

    #
    # Internal operations
    #

    def update(self, a, b):
        a.update(b)
        return a

    def default_config(self):
        return {
            'port': 80,
            'require_auth': False,
            'realm': "esp8266",
            'user': "admin",
            'password': "uhttpD",
            # NB. SSL currently broken
            'use_ssl': False
        }

    def readline(self, client_socket):
        if self._config['use_ssl']:
            import uio
            buf = uio.BytesIO()
            in_newline = False
            done = False
            while not done:
                b = client_socket.read(1)
                buf.write(b)
                #print(buf.getvalue())
                if in_newline:
                    if b == b'\n':
                        done = True
                    else:
                        in_newline = False
                elif b == b'\r':
                    in_newline = True
            return buf.getvalue()
        else:
            return client_socket.readline()

    def parse_heading(self, line):
        ra = line.split()
        try:
            return {
                'verb': ra[0],
                'path': ra[1],
                'protocol': ra[2]
            }
        except:
            raise BadRequestException()

    def parse_header(self, line):
        ra = line.split(":")
        return (ra[0].strip(), ra[1].strip())

    def is_authorized(self, authorization):
        import ubinascii
        try:
            tmp = authorization.split()
            if tmp[0].lower() == "basic":
                str = ubinascii.a2b_base64(tmp[1].strip().encode()).decode()
                ra = str.split(':')
                return ra[0] == self._config['user'] and ra[1] == self._config[
                    'password']
            else:
                raise BadRequestException(
                    "Unsupported authorization method: {}".format(tmp[0]))
        except Exception as e:
            raise BadRequestException(e)

    def server_name(self):
        return "uhttpd/{} (running in your devices)".format(self._version)

    def format_heading(self, code):
        return "HTTP/1.1 {} {}".format(code, self.lookup_code(code))

    def lookup_code(self, code):
        if code == 200:
            return "OK"
        elif code == 40:
            return "Bad Request"
        elif code == 401:
            return "Unauthorized"
        elif code == 404:
            return "Not Found"
        elif code == 500:
            return "Internal Server Error"
        else:
            return "Unknown"

    def format_headers(self, headers):
        ret = ""
        for k, v in headers.items():
            ret += "{}: {}\r\n".format(k, v)
        return ret

    def response(self, client_socket, response):
        self.serialize(client_socket, response)
        return (True, None)

    def serialize(self, stream, response):
        #
        # write the heading and headers
        #
        stream.write("{}\r\n{}\r\n".format(
            self.format_heading(response['code']),
            self.format_headers(self.update(
                response['headers'], {'Server': self.server_name()}
            ))
        ).encode('UTF-8'))
        #
        # Write the body, if it's present
        #
        if 'body' in response:
            body = response['body']
            body(stream)

    def unauthorized_error(self, client_socket):
        headers = {
            'www-authenticate': "Basic realm={}".format(self._config['realm'])
        }
        return self.error(client_socket, 401, "Unauthorized", None, headers)

    def bad_request_error(self, client_socket, e):
        error_message = "Bad Request {}:".format(e)
        return self.error(client_socket, 400, error_message, e)

    def not_found_error(self, client_socket, e):
        error_message = "Not Found: {}".format(e)
        return self.error(client_socket, 404, error_message, e)

    def internal_server_error(self, client_socket, e):
        error_message = "Internal Server Error: {}".format(e)
        return self.error(client_socket, 500, error_message, e)

    def error(self, client_socket, code, error_message, e, headers={}):
        logger.debug(error_message)
        ef = lambda stream: self.stream_error(stream, error_message, e)
        response = self.generate_error_response(code, ef, headers)
        return self.response(client_socket, response)

    def stream_error(self, stream, error_message, e):
        stream.write(error_message)
        if e:
            stream.write('<pre>')
            stream.write(self.stacktrace(e))
            stream.write('</pre>')

    def stacktrace(self, e):
        import uio
        buf = uio.BytesIO()
        sys.print_exception(e, buf)
        return buf.getvalue()

    def generate_error_response(self, code, ef, headers={}):
        data1 = '<html><body><header>uhttpd/{}<hr></header>'.format(
            self._version).encode('UTF-8')
        # message data in ef will go here
        data2 = '</body></html>'.encode('UTF-8')
        body = lambda stream: self.write_html(stream, data1, ef, data2)
        return {
            'code': code,
            'headers': self.update({
                'Content-Type': "text/html",
            }, headers),
            'body': body
        }

    def write_html(self, stream, data1, ef, data2):
        stream.write(data1)
        ef(stream)
        stream.write(data2)


SO_REGISTER_HANDLER = const(20)
CONNECTION_TIMEOUT = const(30)


class TCPServer:
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
        #
        # Start the listening socket.  Handle accepts asynchronously
        # in handle_accept/1
        #
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                       1)
        self._server_socket.bind((self._bind_addr, self._port))
        self._server_socket.listen(0)
        self._server_socket.setsockopt(socket.SOL_SOCKET, SO_REGISTER_HANDLER,
                                       self.handle_accept)
        #
        # Report the interfaces on which we are listening
        #
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
            self._client_socket.close()
        if self._server_socket:
            self._server_socket.close()

    def close(self, socket_):
        logger.debug("Closing socket {}".format(socket_))
        socket_.close()
        self._client_socket = None
