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
import sys
import utcp_server
from ulog import logger
import gc

class NotFoundException(Exception):
    pass


class Server:
    def __init__(self, handlers, port=80, use_ssl=False):
        self._handlers = handlers
        self._port = port
        self._tcp_server = utcp_server.Server(port=port, handler=self, use_ssl=use_ssl)
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
            f = client_socket.makefile('rwb')
            request = self.parse_heading(f.readline().decode('UTF-8'))
            request['remote_addr'] = remote_addr
            #
            # find the handler for the specified path.  If we don't have
            # one registered, return an error
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
                error_message = "No Handler for path {}".format(path)
                logger.debug(error_message)
                error = self.internal_server_error(error_message)
                self.serialize(client_socket, error)
                return (True, None)
            request['relative_path'] = relative_path
            #
            # Otherwise, parse out the headers
            #
            headers = {}
            while True:
                line = f.readline()
                if not line or line == b'\r\n':
                    break
                k, v = self.parse_header(line.decode('UTF-8'))
                headers[k] = v
            request['headers'] = headers
            #
            # If the headers have a content length, then read the body
            #
            content_length = 0
            if 'Content-Length' in headers:
                content_length = int(headers['Content-Length'])
            if content_length > 0:
                body = f.read(content_length)
                request['body'] = body
            #
            # get the response from the active handler and serialize it
            # to the socket
            #
            response = handler.handle_request(request)
            response['headers']['Server'] = "uhttpd/{}".format(self._version)
            return self.response(client_socket, response)
        except NotFoundException as e:
            error_message = "Not Found:".format(e)
            ef = lambda stream : self.stream_error(stream, error_message, e)
            response = self.not_found_error(ef)
            return self.response(client_socket, response)
        except BaseException as e:
            #
            # Any unhandled exception is an internal server error
            #
            sys.print_exception(e)
            error_message = "Internal Server Error: {}".format(e)
            logger.debug(error_message)
            ef = lambda stream: self.stream_error(stream, error_message, e)
            response = self.internal_server_error(ef)
            return self.response(client_socket, response)

    #
    # Internal operations
    #


    def parse_heading(self, line):
        ra = line.split()
        return {
            'verb': ra[0],
            'path': ra[1],
            'protocol': ra[2]
        }

    def parse_header(self, line):
        ra = line.split(":")
        return (ra[0].strip(), ra[1].strip())

    def format_heading(self, code):
        return "HTTP/1.1 {} {}".format(code, self.lookup_code(code))

    def lookup_code(self, code):
        if code == 200:
            return "OK"
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
            self.format_headers(response['headers'])
        ).encode('UTF-8'))
        #
        # Write the body, if it's present
        #
        if 'body' in response:
            body = response['body']
            body(stream)

    def stream_error(self, stream, error_message, e):
        stream.write(error_message)
        stream.write('<pre>')
        sys.print_exception(e, stream.makefile())
        stream.write('</pre>')

    def not_found_error(self, ef):
        return self.generate_error_response(404, ef)

    def internal_server_error(self, ef):
        return self.generate_error_response(500, ef)

    def generate_error_response(self, code, ef):
        data1 = '<html><body><header>uhttpd/{}<hr></header>'.format(self._version).encode('UTF-8')
        ## message data in ef will go here
        data2 = '</body></html>'.encode('UTF-8')
        body = lambda stream: self.doit(stream, data1, ef, data2)
        return {
            'code': code,
            'headers': {
                'Server': "uhttpd/{}".format(self._version),
                'Content-Type': "text/html",
            },
            'body': body
        }

    def doit(self, stream, data1, ef, data2):
        stream.write(data1)
        ef(stream)
        stream.write(data2)
