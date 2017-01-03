##
## Copyright (c) dushin.net  All Rights Reserved
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of dushin.net nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import uhttpd
import network
from ulog import logger


class Handler:
    def __init__(self):
        pass

    #
    # callbacks
    #

    def get(self, api_request):
        logger.info("get {}".format(api_request))
        context = api_request['context']
        return self.get_network_stats(context)

    def post(self, api_request):
        logger.info("post {}".format(api_request))
        return self.save(api_request)

    def put(self, api_request):
        logger.info("put {}".format(api_request))
        return self.save(api_request)

    #
    # read operations
    #

    def get_network_stats(self, context):
        ret = {
            'phy_mode': self.get_phy_mode(),
            'sta': self.get_sta_stats(),
            'ap': self.get_ap_stats()
        }
        for component in context:
            if component in ret:
                ret = ret[component]
            else:
                raise uhttpd.NotFoundException("Bad context: {}".format(context))
        return ret

    def get_sta_stats(self):
        sta = network.WLAN(network.STA_IF)
        return self.get_wlan_stats(sta)

    def get_ap_stats(self):
        ap = network.WLAN(network.AP_IF)
        wlan_stats = self.get_wlan_stats(ap)
        wlan_stats['config'] = self.get_wlan_config_stats(ap)
        return wlan_stats

    def get_wlan_stats(self, wlan):
        if wlan.active():
            ip, subnet, gateway, dns = wlan.ifconfig()
            return {
                'status': self.get_wlan_status(wlan),
                'ifconfig': {
                    'ip': ip,
                    'subnet': subnet,
                    'gateway': gateway,
                    'dns': dns
                }
            }
        else:
            return {}

    def get_wlan_config_stats(self, ap):
        import ubinascii
        return {
            'mac': "0x{}".format(ubinascii.hexlify(ap.config('mac')).decode()),
            'essid': ap.config('essid'),
            'channel': ap.config('channel'),
            'hidden': ap.config('hidden'),
            'authmode': self.get_auth_mode(ap.config('authmode'))
        }

    def get_auth_mode(self, mode):
        if mode == network.AUTH_OPEN:
            return "AUTH_OPEN"
        elif mode == network.AUTH_WEP:
            return "AUTH_WEP"
        elif mode == network.AUTH_WPA_PSK:
            return "AUTH_WPA_PSK"
        elif mode == network.AUTH_WPA2_PSK:
            return "AUTH_WPA2_PSK"
        elif mode == network.AUTH_WPA_WPA2_PSK:
            return "AUTH_WPA_WPA2_PSK"
        else:
            return "Unknown auth_mode: {}".format(mode)

    def get_wlan_status(self, wlan):
        status = wlan.status()
        if status == network.STAT_IDLE:
            return 'STAT_IDLE'
        elif status == network.STAT_CONNECTING:
            return 'STAT_CONNECTING'
        elif status == network.STAT_WRONG_PASSWORD:
            return 'STAT_WRONG_PASSWORD'
        elif status == network.STAT_NO_AP_FOUND:
            return 'STAT_NO_AP_FOUND'
        elif status == network.STAT_CONNECT_FAIL:
            return 'STAT_CONNECT_FAIL'
        elif status == network.STAT_GOT_IP:
            return 'STAT_GOT_IP'
        else:
            return "Unknown wlan status: {}".format(status)

    def get_phy_mode(self):
        phy_mode = network.phy_mode()
        if phy_mode == network.MODE_11B:
            return 'MODE_11B'
        elif phy_mode == network.MODE_11G:
            return 'MODE_11G'
        elif phy_mode == network.MODE_11N:
            return 'MODE_11N'
        else:
            return "Unknown phy_mode: {}".format(phy_mode)

    #
    # save operations
    #

    def save(self, api_request):
        context = api_request['context']
        logger.info("context: {}".format(context))
        if context == ['ap', 'config']:
            return self.save_ap_config(api_request)
        else:
            raise uhttpd.BadRequestException("Unsupported context on save: {}", context)

    def save_ap_config(self, api_request):
        config = api_request['body']
        ap = network.WLAN(network.AP_IF)
        logger.info("config: {}".format(config))
        ap.config(
            #mac=config['mac'],
            essid=config['essid'],
            channel=config['channel'],
            hidden=config['hidden']
        )
        return self.get_wlan_config_stats(ap)
