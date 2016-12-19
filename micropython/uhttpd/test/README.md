# Testing

You can use the `test_server.py` and `test_client.py` scripts to test the `uhttpd` server.

## Server-side

Upload `test_server.py` to your ESP8266 using `webrepl` or equivalent, and run the following commands:

    >>> import test_server
    >>> test_server.init()
    Initializing...
    >>> test_server.start()
    Starting test server ...
    loaded sink console
    2000-01-01T15:45:02.005 [info] esp8266: uhttpd-master started.

The ESP8266 is now ready to test.

## Client-side

Client side tests should be run on your local machine, not on the ESP8266.  The `test-client.py` script requires python3 or later.

You must specify the IP address of your ESP8266, e.g.,

    prompt$ python3 test_client.py 192.168.1.180
    ....................
    ----------------------------------------------------------------------
    Ran 20 tests in 3.631s

    OK

On the ESP8266 you should see something like the following printed to the console:

    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59272)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59273)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59274)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59275)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59276)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59277)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59278)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59279)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59280)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59281)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59282)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59283)
    2000-01-01T00:09:44.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59284)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59285)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59286)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59287)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59288)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59289)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59290)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59291)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59292)
    2000-01-01T00:09:45.005 [info] esp8266: UNAUTHORIZED ('192.168.1.154', 59293)
    2000-01-01T00:09:45.005 [info] esp8266: UNAUTHORIZED ('192.168.1.154', 59294)
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59295)
    2000-01-01T00:09:45.005 [info] esp8266: ACCESS ('192.168.1.154', 59295) /www/index.html
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59296)
    2000-01-01T00:09:45.005 [info] esp8266: ACCESS ('192.168.1.154', 59296) /www/index.html
    2000-01-01T00:09:45.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59297)
    2000-01-01T00:09:45.005 [info] esp8266: ACCESS ('192.168.1.154', 59297) /www/foo
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59298)
    2000-01-01T00:09:46.005 [info] esp8266: ACCESS ('192.168.1.154', 59298) /www/index.html
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59299)
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59300)
    2000-01-01T00:09:46.005 [info] esp8266: ACCESS ('192.168.1.154', 59300) /www/foo/bar/test.js
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59301)
    2000-01-01T00:09:46.005 [info] esp8266: ACCESS ('192.168.1.154', 59301) /www/foo/bar/test.css
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59305)
    2000-01-01T00:09:46.005 [info] esp8266: NOT_FOUND ('192.168.1.154', 59305) /www/bar
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59306)
    2000-01-01T00:09:46.005 [info] esp8266: FORBIDDEN ('192.168.1.154', 59306) /
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59307)
    2000-01-01T00:09:46.005 [info] esp8266: ACCESS ('192.168.1.154', 59307) /www/foo/test.txt
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59308)
    2000-01-01T00:09:46.005 [info] esp8266: ACCESS ('192.168.1.154', 59308) /www/foo/test.txt
    2000-01-01T00:09:46.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59310)
    2000-01-01T00:09:47.005 [info] esp8266: ACCESS ('192.168.1.154', 59310) /www/foo/test.txt
    2000-01-01T00:09:47.005 [info] esp8266: AUTHORIZED ('192.168.1.154', 59311)
    2000-01-01T00:09:47.005 [info] esp8266: ACCESS ('192.168.1.154', 59311) /www/foo/bar
