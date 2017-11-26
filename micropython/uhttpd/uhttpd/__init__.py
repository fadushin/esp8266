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
import logging
import gc
import uasyncio as asyncio

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
            #timeout=self._config['timeout'],
            handler=self,
            backlog=self._config['backlog']
        )

    #
    # API
    #

    def run(self):
        logging.info("uhttpd-{} running...".format(VERSION))
        self._tcp_server.run()

    #
    # Callbacks
    #

    def handle_request(self, reader, writer, tcp_request):
        http_request = {
            'tcp': tcp_request
        }
        try:
            #
            # parse out the heading line, to get the verb, path, and protocol
            #
            line = yield from reader.readline()
            heading = self.parse_heading(line.decode('UTF-8'))
            #logging.debug("Parsed heading {}".format(heading))
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
                    #logging.debug("Found handler for prefix {}".format(prefix))
                    break
            #
            # Parse out the headers
            #
            headers = {}
            num_headers = 0
            while True:
                line = yield from reader.readline()
                if not line or line == b'\r\n':
                    break
                k, v = Server.parse_header(line.decode('UTF-8'))
                headers[k.lower()] = v
                num_headers += 1
                if num_headers > self._config['max_headers']:
                    raise BadRequestException("Number of headers exceeds maximum allowable")
            #logging.debug("Parsed headers {}".format(headers))
            http_request['headers'] = headers
            #
            # If the headers have a content length, then read the body
            #
            #content_length = 0
            if 'content-length' in headers:
                content_length = int(headers['content-length'])
                #logging.debug("content_length: {}".format(content_length))
                if content_length > self._config['max_content_length']:
                    raise BadRequestException("Content size exceeds maximum allowable")
                elif content_length > 0:
                    body = yield from reader.read(content_length)
                    #logging.debug("Read body: {}".format(body))
                    http_request['body'] = body
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
                    return (yield from self.unauthorized_error(writer))
                else:
                    remote_addr = tcp_request['remote_addr']
                    is_authorized, user = self.is_authorized(headers['authorization'])
                    if not is_authorized:
                        logging.info("UNAUTHORIZED {}".format(remote_addr))
                        return (yield from self.unauthorized_error(writer))
                    else:
                        logging.info("AUTHORIZED {}".format(remote_addr))
                        http_request['user'] = user
            #
            # get the response from the active handler and serialize it
            # to the socket
            #
            response = handler.handle_request(http_request)
            return (yield from Server.response(writer, response))
        except BadRequestException as e:
            return (yield from Server.bad_request_error(writer, e))
        except ForbiddenException as e:
            return (yield from Server.forbidden_error(writer, e))
        except NotFoundException as e:
            return (yield from Server.not_found_error(writer, e))
        except BaseException as e:
            return (yield from Server.internal_server_error(writer, e))

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
            #'timeout': 30,
            'require_auth': False,
            'realm': "esp8266",
            'user': "admin",
            'password': "uhttpD",
            'max_headers': 25,
            'max_content_length': 1024,
            'backlog': 5
        }

    #def readline(self, client_socket):
    #    return client_socket.readline()

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
        return "HTTP/1.1 {} {}".format(code, Server.lookup_code(code))

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
    def response(client_socket, response):
        yield from Server.serialize(client_socket, response)
        return (True, None)

    @staticmethod
    def serialize(stream, response):
        #
        # write the heading and headers
        #
        yield from stream.awrite("{}\r\n{}\r\n".format(
            Server.format_heading(response['code']),
            Server.format_headers(Server.update(
                response['headers'], {'Server': Server.server_name()}
            ))
        ).encode('UTF-8'))
        #
        # Write the body, if it's present
        #
        if 'body' in response:
            body = response['body']
            if body:
                yield from body(stream)

    def unauthorized_error(self, writer):
        headers = {
            'www-authenticate': "Basic realm={}".format(self._config['realm'])
        }
        return Server.error(writer, 401, "Unauthorized", None, headers)

    @staticmethod
    def bad_request_error(writer, e):
        error_message = "Bad Request {}:".format(e)
        return (yield from Server.error(writer, 400, error_message, e))

    @staticmethod
    def forbidden_error(writer, e):
        error_message = "Forbidden {}:".format(e)
        return (yield from Server.error(writer, 403, error_message, e))

    @staticmethod
    def not_found_error(writer, e):
        error_message = "Not Found: {}".format(e)
        return (yield from Server.error(writer, 404, error_message, e))

    @staticmethod
    def internal_server_error(writer, e):
        sys.print_exception(e)
        error_message = "Internal Server Error: {}".format(e)
        return (yield from Server.error(writer, 500, error_message, e))

    @staticmethod
    def error(writer, code, error_message, e, headers={}):
        #logging.debug("Error!  code: {} error_message: {} exception: {}".format(code, error_message, e))
        ef = lambda stream: (yield from Server.stream_error(writer, error_message, e))
        response = Server.generate_error_response(code, ef, headers)
        return (yield from Server.response(writer, response))

    @staticmethod
    def stream_error(writer, error_message, e):
        yield from writer.awrite(error_message)
        if e:
            yield from writer.awrite('<pre>')
            yield from writer.awrite(Server.stacktrace(e))
            yield from writer.awrite('</pre>')

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
        body = lambda writer: (yield from Server.write_html(writer, data1, ef, data2))
        return {
            'code': code,
            'headers': Server.update({
                'content-type': "text/html",
            }, headers),
            'body': body
        }

    @staticmethod
    def write_html(writer, data1, ef, data2):
        yield from writer.awrite(data1)
        yield from ef(writer)
        yield from writer.awrite(data2)


class TCPServer:
    def __init__(self, port, handler, bind_addr='0.0.0.0',
                 #timeout=30,
                 backlog=10):
        self._port = port
        self._handler = handler
        self._bind_addr = bind_addr
        #self._timeout = timeout
        self._backlog = backlog

    def handle_receive(self, reader, writer, tcp_request):
        try:
            done, response = yield from self._handler.handle_request(reader, writer, tcp_request)
            if response and len(response) > 0:
                yield from writer.awrite(response)
            if done:
                return False
            else:
                return True
        except Exception as e:
            sys.print_exception(e)
            return False

    def serve(self, reader, writer):
        tcp_request = {
            'remote_addr': writer.extra["peername"]
        }
        gc.collect()
        try:
            while (yield from self.handle_receive(reader, writer, tcp_request)):
                gc.collect()
        finally:
            yield from writer.aclose()
            gc.collect()

    def run(self, debug=False):
        if debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)

        loop = asyncio.get_event_loop()
        this = self

        @asyncio.coroutine
        def serve(reader, writer):
            yield from this.serve(reader, writer)

        loop.call_soon(asyncio.start_server(
            client_coro=serve,
            host=self._bind_addr,
            port=self._port,
            backlog=self._backlog
        ))
        loop.run_forever()
        loop.close()


#class EchoHandler:
#    def __init__(self):
#        pass
#
#    def handle_request(self, reader, writer, tcp_request):
#        data = yield from reader.readline()
#        return False, data



#def test():
#    server = TCPServer(port=80, handler=EchoHandler())
#   server.run()





