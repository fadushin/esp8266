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
import logging
import uhttpd

class Handler :
    
    def __init__(self, controller, verbose=False):
        self.controller = controller
        self.verbose = verbose

    def get(self, api_request):
        context = api_request['context']
        if len(context) > 0 :
            if context[0] == 'config' :
                return Handler.get_path(self.controller.config, context[1:])
            if context[0] == 'stats' :
                return self.controller.get_stats()
        else :
            return self.get_color()
                
    def get_color(self):
        data = []
        for i in range(self.controller.np.n) :
            data.append({
                "r": self.controller.np[i][0],
                "g": self.controller.np[i][1],
                "b": self.controller.np[i][2]
            })
        return {
            "n": len(data),
            "data": data
        }
        
    @staticmethod
    def get_path(tree, path) :
        for c in path :
            if c in tree :
                tree = tree[c]
            else :
                raise uhttpd.NotFoundException("Invalid path: {}; '{}' not found.".format(path, c))
        return Handler.serialize(tree)
    
    @staticmethod
    def serialize(node) :
        node_type = type(node)
        if node_type is dict :
            return Handler.list_keys(node)
        else :
            return node
    
    @staticmethod
    def list_keys(node) :
        ret = []
        for key in node.keys() :
            ret.append(key)
        return ret

    def post(self, api_request):
        if self.verbose :
            logging.info('post: api_request={}', api_request)
        context = api_request['context']
        if len(context) > 0 :
            query_params = api_request['query_params']
            operator = context[0]
            if operator == 'mode' :
                self.controller.set_mode(query_params['mode'])
            elif operator == 'np' :
                pin = None
                num_pixels = None
                if 'pin' in query_params :
                    pin = query_params['pin']
                if 'num_pixels' in query_params :
                    num_pixels = query_params['num_pixels']
                self.controller.set_np(pin=pin, num_pixels=num_pixels)
            elif operator == 'lamp' :
                self.controller.set_color_name(query_params['color_name'])
            elif operator == 'schedule' :
                if 'name' not in query_params :
                    raise uhttpd.BadRequestException("Expected name in query_params")
                self.controller.update_schedule(query_params['name'], api_request['body'])
            elif operator == 'colorspec' :
                self.controller.set_colorspec(api_request['body'])
            elif operator == 'color' :
                self.controller.set_color((
                    int(query_params['r']),
                    int(query_params['g']),
                    int(query_params['b'])
                ))
            elif operator == 'reboot' :
                self.controller.reboot()
            elif operator == 'reset' :
                self.controller.reset()
            else :
                raise uhttpd.BadRequestException("Bad post request: Unknown operator: {}".format(operator))
        else :
            raise uhttpd.BadRequestException("Bad post request: Missing operator in context")

    def delete(self, api_request):
        context = api_request['context']
        if len(context) > 0 :
            query_params = api_request['query_params']
            operator = context[0]
            if operator == 'schedule' :
                if 'name' not in query_params :
                    raise uhttpd.BadRequestException("Expected name in query_params")
                self.controller.delete_schedule(query_params['name'])
            else :
                raise uhttpd.BadRequestException("Bad delete request: Unknown operator: {}".format(operator))
        else :
            raise uhttpd.BadRequestException("Bad delete request: Missing operator in context")
