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
import utcp_server

class Server :
    
    def __init__(self, handlers, port = 80) :
        self._handlers = handlers
        self._port = port
        self._tcp_server = utcp_server.Server(port, self)
    
    ##
    ## API
    ##
    
    def start(self) :
        '''Start the server'''
        self._tcp_server.start()

    ##
    ## Callbacks
    ##
    
    def handle_request(self, client_socket) :
        try :
            ##
            ## parse out the heading line, to get the verb, path, and protocol
            ##
            f = client_socket.makefile('rwb')
            request = self.parse_heading(f.readline().decode('UTF-8'))
            ##
            ## find the handler for the specified path.  If we don't have
            ## one registered, return an error
            ##
            path = request['path']
            handler = None
            for prefix, h in self._handlers :
                if path.startswith(prefix) :
                    handler = h
                    break
            if not handler :
                error = self.internal_server_error(
                    "No Handler for path {}".format(path)
                )
                self.serialize(client_socket, error)
                return (True, None)
            ##
            ## Otherwise, parse out the headers
            ##
            headers = {}
            while True :
                line = f.readline()
                if not line or line == b'\r\n':
                    break
                k, v = self.parse_header(line.decode('UTF-8'))
                headers[k] = v
            request['headers'] = headers
            ##
            ## If the headers have a content length, then read the body
            ##
            content_length = 0
            if 'Content-Length' in headers :
                content_length = int(headers['Content-Length'])
            if content_length > 0 :
                body = f.read(content_length)
                request['body'] = body
            ##
            ## get the response from the active handler and serialize it
            ## to the socket
            ##
            response = handler.handle_request(request)
            self.serialize(client_socket, response)
            return (True, None)
        except BaseException as e :
            ##
            ## Any unhandled exception is an internal server error
            ##
            error = self.internal_server_error(
                "An error occurred parsing HTTP payload: `{}`".format(e)
            )
            self.serialize(client_socket, error)
            return (True, None)
    
    ##
    ## Internal operations
    ##
    
    def parse_heading(self, line) :
        ra = line.split()
        return {
            'verb': ra[0],
            'path': ra[1],
            'protocol': ra[2]
        }
    
    def parse_header(self, line) :
        ra = line.split(":")
        return (ra[0].strip(), ra[1].strip())
    
    def format_heading(self, code) :
        return "HTTP/1.1 {} OK".format(code)
    
    def format_headers(self, headers) :
        ret = ""
        for k, v in headers.items() :
            ret += "{}: {}\r\n".format(k, v)
        return ret
    
    def serialize(self, stream, response) :
        ##
        ## write the heading and headers
        ##
        stream.write("{}\r\n{}\r\n".format(
            self.format_heading(response['code']), 
            self.format_headers(response['headers'])
        ).encode('UTF-8'))
        ##
        ## Write the body, if it's present
        ##
        if 'body' in response :
            body = response['body']
            body(stream)

    def internal_server_error(self, message) :
        data = "<html><body>Internal Server Error: {}</body></html>".format(message).encode('UTF-8')
        body = lambda stream : stream.write(data)
        return {
            'code': 500, 
            'headers': {
                'Content-Type': "text/html"
            }, 
            'body': body
        }
        


class TestHandler :
    
    def __init__(self) :
        pass
    
    def handle_request(self, request) :
        data = "<html><body>Hello World!</body></html>\n".encode('UTF-8')
        body = lambda stream : stream.write(data)
        return {
            'code': 200, 
            'headers': {
                'Content-Type': "text/html",
                'Content-Length': len(data)
            }, 
            'body': body}

#import http_file_handler
#server = Server([
#    ('/test', TestHandler()),
#    ('/', http_file_handler.Handler())
#])
