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

import json
from ulog import logger
import uhttpd

class Handler:
    def __init__(self, handlers):
        """
        :param handlers:  a dictionary from [string()] -> RestHandler
        """
        self._handlers = handlers

    #
    # callbacks
    #

    def handle_request(self, request):
        relative_path = request['relative_path']
        components = relative_path.strip('/').split('/')
        handler, context = self.find_handler(components)
        if handler:
            logger.debug("Found api_handler {}".format(handler.module()))
            verb = request['verb'].lower()
            if 'body' in request:
                try:
                    request['body'] = json.loads(request['body']) if request['body'].trim() else None
                except:
                    raise uhttpd.BadRequestException("Malformed JSON body")
            if verb == 'get':
                logger.debug("Verb is 'get'")
                response = handler.get(context, request)
            elif verb == 'put':
                logger.debug("Verb is put'")
                response = handler.put(context, request)
            elif verb == 'post':
                logger.debug("Verb is post'")
                response = handler.post(context, request)
            elif verb == 'delete':
                logger.debug("Verb is delete'")
                response = handler.delete(context, request)
            else:
                # TODO add support for more verbs!
                error_message = "Unsupported verb: {}".format(verb)
                logger.debug(error_message)
                raise uhttpd.BadRequestException(error_message)
        else:
            error_message = "No handler found for components {}".format(
                components)
            logger.debug(error_message)
            raise uhttpd.NotFoundException(error_message)
        data = json.dumps(response).encode('UTF-8')
        body = lambda stream: stream.write(data)
        return {
            'code': 200,
            'headers': {
                'Content-Type': "application/json",
                'Content-Length': len(data)
            },
            'body': body
        }

    def module(self):
        return 'api_handler'

    #
    # Internal operations
    #

    def find_handler(self, components):
        for prefix, handler in self._handlers:
            if self.sublist(prefix, components):
                return (handler, components[len(prefix):])
        return (None, None)

    def sublist(self, l1, l2):
        return l1 == l2[:len(l1)]
