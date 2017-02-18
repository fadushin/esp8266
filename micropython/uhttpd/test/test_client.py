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
import unittest

#host = "localhost"
host = "192.168.1.174"
#host = "192.168.1.180"

class Connection:

    def __init__(self, host, port=80):
        self.connection = None
        self.host = host
        self.port = int(port)

    def get(self, context='/', headers={}, body=None):
        return self.request("GET", context, headers=headers)

    def put(self, context='/', headers={}, body=None):
        return self.request("PUT", context, body=body, headers=headers)

    def post(self, context='/', headers={}, body=None):
        return self.request("POST", context, body=body, headers=headers)

    def delete(self, context='/', headers={}, body=None):
        return self.request("DELETE", context, body=body, headers=headers)

    def request(self, verb, context, body=None, headers={}):
        import http.client
        connection = http.client.HTTPConnection(self.host, self.port)
        connection.request(verb, context, body=body, headers=headers)
        response = connection.getresponse()
        body = response.read()
        ret = {
            'status': response.status,
            'headers': response.getheaders(),
            'body': body
        }
        connection.close()
        return ret


def get_header(el, name):
    for k, v in el:
        if k == name:
            return v
    return None


def make_headers(size):
    ret = {}
    for i in range(size):
        ret[str(i)] = str(i)
    return ret


def basic_auth_headers(username, password):
    import binascii
    basic_auth_token = binascii.b2a_base64("{}:{}".format(username, password).encode()).decode().strip()
    return {
        'authorization': "Basic {}".format(basic_auth_token)
    }




class HttpdTest(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self._connection = Connection(host)

    def test_no_handler(self):
        self.verify_get('/', expected_status=404, expected_content_type='text/html')

    def test_default_index_html(self):
        self.verify_get('/test', expected_status=200, expected_content_type='text/html')

    def test_explicit_index_html(self):
        self.verify_get('/test/index.html', expected_status=200, expected_content_type='text/html')

    def test_dir_listing(self):
        self.verify_get('/test/foo', expected_status=200, expected_content_type='text/html')

    def test_not_found(self):
        self.verify_get('/test/bar', expected_status=404, expected_content_type='text/html')

    def test_plaintext_file(self):
        self.verify_get('/test/foo/test.txt', expected_status=200, expected_content_type='text/plain', expected_body=b'test')

    def test_relative_path(self):
        self.verify_get('/test/foo/bar/../test.txt', expected_status=200, expected_content_type='text/plain', expected_body=b'test')
        self.verify_get('/test/foo/does-not-exist/../test.txt', expected_status=200, expected_content_type='text/plain', expected_body=b'test')
        self.verify_get('/test/foo/bar', expected_status=200, expected_content_type='text/html')

    def test_file_types(self):
        self.verify_get('/test/foo/bar/test.js', expected_status=200, expected_content_type='text/javascript', expected_body=b'{\'foo\': "bar"}')
        self.verify_get('/test/foo/bar/test.css', expected_status=200, expected_content_type='text/css', expected_body=b'html')

    def test_out_of_range(self):
        self.verify_get('/test/..', expected_status=403, expected_content_type='text/html')

    def test_max_headers(self):
        # server should drop the connection
        with self.assertRaises(ConnectionResetError):
            self.verify_get('/test', expected_status=400, additional_headers=make_headers(55))

    def test_max_body(self):
        # server should drop the connection
        with self.assertRaises(ConnectionResetError):
            self.verify_put('/test', expected_status=400, body=bytearray(2048))

    def test_file_handler_put_fail(self):
        # should be a bad request
        self.verify_put('/test', expected_status=400, expected_content_type='text/html')

    def test_auth(self):
        self.verify_get('/test', expected_status=401, expected_content_type='text/html', additional_headers=basic_auth_headers('admin', 'bad-password'))
        self.verify_get('/test', expected_status=401, expected_content_type='text/html', additional_headers=basic_auth_headers('unknown-user', 'knockknock'))
        self.verify_get('/test', expected_status=200, expected_content_type='text/html', additional_headers=basic_auth_headers('admin', 'uhttpD'))

    def test_api_json_body(self):
        self.verify_put('/api/test', expected_status=200, body="this is clearly not JSON", additional_headers={'content-type': "text/plain"})
        self.verify_put('/api/test', expected_status=400, body="this is clearly not JSON", additional_headers={'content-type': "application/json"})

    def test_api_no_handler(self):
        self.verify_put('/api/foo', expected_status=404, expected_content_type='text/html')

    def test_api_actions(self):
        self.verify_get('/api/test', expected_status=200, expected_content_type='application/json', expected_body=b'{"action": "get"}')
        self.verify_get('/api/test/foo', expected_status=200, expected_content_type='application/json', expected_body=b'{"action": "get"}')
        self.verify_put('/api/test', expected_status=200, expected_content_type='application/json', expected_body=b'{"action": "put"}')
        self.verify_post('/api/test', expected_status=200, expected_content_type='application/json', expected_body=b'{"action": "post"}')
        self.verify_delete('/api/test', expected_status=200, expected_content_type='application/json', expected_body=b'{"action": "delete"}')

    def test_api_bad_query_params(self):
        self.verify_get('/api/test?foo', expected_status=400, expected_content_type='text/html')
        self.verify_get('/api/test?foo?', expected_status=400, expected_content_type='text/html')
        self.verify_get('/api/test?=bar', expected_status=400, expected_content_type='text/html')
        self.verify_get('/api/test?foo=bar=tapas', expected_status=400, expected_content_type='text/html')

    def test_api_query_params(self):
        self.verify_get('/api/test/query_params?', expected_status=200, expected_content_type='application/json', expected_body=b'{}')
        self.verify_get('/api/test/query_params?&&&&', expected_status=200, expected_content_type='application/json', expected_body=b'{}')
        self.verify_get('/api/test/query_params?foo=bar&gnu=gnat', expected_status=200, expected_content_type='application/json', expected_body=b'{"gnu": "gnat", "foo": "bar"}')

    def test_api_return(self):
        self.verify_get('/api/test/nothing', expected_status=200, expected_content_type=None, expected_body=None)
        self.verify_get('/api/test/empty', expected_status=200, expected_content_type="application/binary", expected_body=b'')
        self.verify_get('/api/test/something', expected_status=200, expected_content_type="application/binary", expected_body=b'something')

    def test_api_exception(self):
        self.verify_get('/api/test/bad_request_excetion', expected_status=400, expected_content_type="text/html")
        self.verify_get('/api/test/not_found_excetion', expected_status=404, expected_content_type="text/html")
        self.verify_get('/api/test/forbidden_excetion', expected_status=403, expected_content_type="text/html")

    def verify_get(
        self, context, body=None, additional_headers={},
        expected_status=None, expected_content_type=None, expected_body=None

    ):
        return self.verify_action(
            lambda headers: self._connection.get(context, headers, body),
            additional_headers=additional_headers,
            expected_status=expected_status,
            expected_content_type=expected_content_type,
            expected_body=expected_body
        )

    def verify_put(
        self, context, body=None, additional_headers={},
        expected_status=None, expected_content_type=None, expected_body=None

    ):
        return self.verify_action(
            lambda headers: self._connection.put(context, headers, body),
            additional_headers=additional_headers,
            expected_status=expected_status,
            expected_content_type=expected_content_type,
            expected_body=expected_body
        )

    def verify_post(
        self, context, body=None, additional_headers={},
        expected_status=None, expected_content_type=None, expected_body=None

    ):
        return self.verify_action(
            lambda headers: self._connection.post(context, headers, body),
            additional_headers=additional_headers,
            expected_status=expected_status,
            expected_content_type=expected_content_type,
            expected_body=expected_body
        )

    def verify_delete(
        self, context, body=None, additional_headers={},
        expected_status=None, expected_content_type=None, expected_body=None

    ):
        return self.verify_action(
            lambda headers: self._connection.delete(context, headers, body),
            additional_headers=additional_headers,
            expected_status=expected_status,
            expected_content_type=expected_content_type,
            expected_body=expected_body
        )

    def verify_action(
        self, action,
        expected_status=None, expected_content_type=None, expected_body=None,
        additional_headers={}
    ):
        headers = basic_auth_headers("admin", "uhttpD")
        headers.update(additional_headers)
        response = action(headers)
        if expected_status:
            self.assertEqual(response['status'], expected_status)
        if expected_content_type:
            self.assertEqual(get_header(response['headers'], 'content-type'), expected_content_type)
        if expected_body:
            self.assertEqual(response['body'], expected_body)


    def test_concurrent_file(self):
        import threading
        threads = []
        for i in range(3):
            t = threading.Thread(target=self.get_test_js)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def get_test_js(self):
        import time
        for i in range(10):
            self.verify_get('/test/foo/bar/test.js', expected_status=200, expected_content_type='text/javascript', expected_body=b'{\'foo\': "bar"}')
            time.sleep(0.1)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Syntax: test_client.py <host>")
        sys.exit(1)
    host = sys.argv.pop()
    unittest.main()
