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
import os
from ulog import logger
import uhttpd

CONTENT_TYPE_MAP = {
    ".html": "text/html",
    ".js": "text/javascript",
    ".css": "text/css"
}


class Handler:
    def __init__(self, root_path='/www', block_size=1024):
        if not self.exists(root_path) or not self.is_dir(root_path):
            msg = "Root path {} is not an existing directory".format(root_path)
            raise Exception(msg)
        self._root_path = root_path
        self._block_size = block_size

    #
    # callbacks
    #

    def handle_request(self, request):
        #
        # We only support GET
        #
        verb = request['verb']
        if verb.lower() != 'get':
            return self.create_message_response(
                500, "Unsupported verb: {}".format(verb)
            )
        #
        # If the path doesn't exist, 404 out
        #
        path = request['path']
        full_path = "{}{}".format(self._root_path, path).rstrip('/')
        if not self.exists(full_path):
            logger.info(
                "NOT_FOUND {} {}".format(request['remote_addr'], full_path))
            raise uhttpd.NotFoundException(full_path)
        #
        # Otherwise, generate a file listing or a file
        #
        if self.is_dir(full_path):
            logger.debug("{} is a directory.".format(full_path))
            index_path = full_path + "/index.html"
            if self.exists(index_path):
                response = self.create_file_response(index_path)
                logger.info(
                    "ACCESS {} {}".format(request['remote_addr'], index_path))
                return response
            else:
                logger.info(
                    "ACCESS {} {}".format(request['remote_addr'], full_path))
                return self.create_dir_listing_response(full_path, path)
        else:
            logger.info(
                "ACCESS {} {}".format(request['remote_addr'], full_path))
            return self.create_file_response(full_path)

    def module(self):
        return 'http_file_handler'

    #
    # internal operations
    #

    def is_dir(self, path):
        try:
            os.listdir(path)
            return True
        except OSError:
            return False

    def exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def create_message_response(self, code, message):
        data = "<html><body>{}</body></html>".format(message).encode('UTF-8')
        length = len(data)
        body = lambda stream: stream.write(data)
        return self.create_response(code, "text/html", length, body)

    def create_file_response(self, path):
        length, body = self.generate_file(path)
        suffix = self.get_suffix(path)
        if suffix in CONTENT_TYPE_MAP:
            content_type = CONTENT_TYPE_MAP[suffix]
        else:
            content_type = "text/plain"
        return self.create_response(200, content_type, length, body)

    def generate_file(self, path):
        f = open(path, 'r')
        serializer = lambda stream: self.stream_file(stream, f)
        return (self.file_size(path), serializer)

    def create_dir_listing_response(self, full_path, path):
        length, body = self.generate_dir_listing(path, os.listdir(full_path))
        return self.create_response(200, "text/html", length, body)

    def generate_dir_listing(self, path, files):
        data = "<html><body><header><em>uhttpd/{}</em><hr></header><h1>{}</h1><ul>".format("pre-0.1", path)
        if path != '/':
            components = path.strip('/').split('/')
            components = components[:len(components)-1]
            data += "<li><a href=\"{}\">..</a></li>\n".format("/{}".format("/".join(components)))
        for f in files:
            data += "<li><a href=\"{}\">{}</a></li>\n".format(path[1:] + '/' + f, f)
        data += "</ul></body></html>"
        data = data.encode('UTF-8')
        body = lambda stream: stream.write(data)
        return (len(data), body)

    def create_response(self, code, content_type, length, body):
        return {
            'code': code,
            'headers': {
                'Content-Type': content_type,
                'Content-Length': length
            },
            'body': body
        }

    def stream_file(self, stream, f):
        while True:
            buf = f.read(self._block_size)
            if buf:
                stream.write(buf)
            else:
                break

    def file_size(self, path):
        return os.stat(path)[6]

    def get_suffix(self, path):
        idx = path.rfind('.')
        return "" if idx == -1 else path[idx:]
