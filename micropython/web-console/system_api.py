#
# Copyright (c) dushin.net  All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of dushin.net nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
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
import uhttpd
import machine
import ubinascii
import sys


class Handler:
    def __init__(self):
        pass

    #
    # callbacks
    #

    def get(self, api_request):
        context = api_request['context']
        return self.get_sys_stats(context)

    #
    # read operations
    #

    def get_sys_stats(self, context):
        ret = {
            'machine_id': "0x{}".format(ubinascii.hexlify(machine.unique_id()).decode().upper()),
            'machine_freq': machine.freq(),
            'byteorder': sys.byteorder,
            'system': "{}-{}".format(
                sys.implementation[0],
                self.to_version_string(sys.implementation[1]),
            ),
            'maxsize': sys.maxsize,
            'modules': self.keys(sys.modules),
            'path': sys.path,
            'platform': sys.platform,
            'version': sys.version,
        }
        for component in context:
            if component in ret:
                ret = ret[component]
            else:
                raise uhttpd.NotFoundException("Bad context: {}".format(context))
        return ret

    def keys(self, pairs):
        ret = []
        for k, v in pairs.items():
            ret.append(k)
        return ret

    def to_version_string(self, version):
        return "{}.{}.{}".format(
            version[0], version[1], version[2]
        )
