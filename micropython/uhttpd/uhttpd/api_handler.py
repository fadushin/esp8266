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
import ujson
import uhttpd


class Handler:
    def __init__(self, handlers):
        self._handlers = handlers

    #
    # callbacks
    #

    def handle_request(self, http_request):
        relative_path = uhttpd.get_relative_path(http_request)
        path_part, query_params = self.extract_query(relative_path)
        components = path_part.strip('/').split('/')
        prefix, handler, context = self.find_handler(components)
        if handler:
            json_body = None
            headers = http_request['headers']
            if 'body' in http_request and 'content-type' in headers and headers['content-type'] == "application/json":
                try:
                    json_body = ujson.loads(http_request['body'])
                except Exception as e:
                    raise uhttpd.BadRequestException("Failed to load JSON: {}".format(e))
            verb = http_request['verb']
            api_request = {
                'prefix': prefix,
                'context': context,
                'query_params': query_params,
                'body': json_body,
                'http': http_request
            }
            if verb == 'get':
                response = handler.get(api_request)
            elif verb == 'put':
                response = handler.put(api_request)
            elif verb == 'post':
                response = handler.post(api_request)
            elif verb == 'delete':
                response = handler.delete(api_request)
            elif verb == 'options':
                response = handler.options(api_request)
            else:
                # TODO add support for more verbs!
                error_message = "Unsupported verb: {}".format(verb)
                raise uhttpd.BadRequestException(error_message)
        else:
            error_message = "No handler found for components {}".format(components)
            raise uhttpd.NotFoundException(error_message)
        ##
        ## prepare response
        ##
        if response is not None:
            response_type = type(response)
            if response_type is dict or response_type is list:
                data = ujson.dumps(response).encode('UTF-8')
                body = lambda stream : stream.awrite(data)
                content_type = "application/json"
                content_length = len(data)
            elif response_type is bytes:
                data = response
                body = lambda stream : stream.awrite(data)
                content_type = "application/binary"
                content_length = len(data)
            elif response_type is str:
                data = response.encode("UTF-8")
                body = lambda stream : stream.awrite(data)
                content_type = "text/html; charset=utf-8"
                content_length = len(data)
            elif response_type is int or response_type is float: 
                data = str(response)
                body = lambda stream : stream.awrite(data)
                content_type = "text/plain"
                content_length = len(data)
            else :
                data = str(response)
                body = lambda stream : stream.awrite(data)
                content_type = "text/plain"
                content_length = len(data)
        else:
            body = None
            content_type = None
            content_length = None
        headers = {}
        if content_length :
            headers.update({'content-length': content_length})
        if content_type:
            headers.update({'content-type': content_type})
        return {
            'code': 200,
            'headers': headers,
            'body': body
        }

    #
    # Internal operations
    #

    def find_handler(self, components):
        for prefix, handler in self._handlers:
            prefix_len = len(prefix)
            if prefix == components[:prefix_len]:
                return prefix, handler, components[prefix_len:]
        return None, None, None

    @staticmethod
    def extract_query(path):
        components = path.split("?")
        query_params = {}
        if len(components) == 1:
            return path, query_params
        elif len(components) > 2:
            raise uhttpd.BadRequestException("Malformed path: {}".format(path))
        path_part = components[0]
        query_part = components[1]
        qparam_components = query_part.split("&")
        for qparam_component in qparam_components:
            if qparam_component.strip() == '':
                continue
            qparam = qparam_component.split("=")
            if len(qparam) != 2 or not qparam[0]:
                raise uhttpd.BadRequestException("Invalid query parameter: {}".format(qparam_component))
            query_params[qparam[0]] = qparam[1]
        return path_part, query_params
