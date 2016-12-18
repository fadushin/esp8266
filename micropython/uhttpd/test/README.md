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
    ................
    ----------------------------------------------------------------------
    Ran 16 tests in 3.018s
    
    OK

On the ESP8266 you should see something like the following printed to the console:

    2000-01-02T09:36:58.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63573)
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63575)
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63576)
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63577)
    2000-01-02T09:36:59.006 [info] esp8266: UNAUTHORIZED ('192.168.1.154', 63578)
    2000-01-02T09:36:59.006 [info] esp8266: UNAUTHORIZED ('192.168.1.154', 63579)
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63580)
    2000-01-02T09:36:59.006 [info] esp8266: ACCESS ('192.168.1.154', 63580) /www/index.html
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63581)
    2000-01-02T09:36:59.006 [info] esp8266: ACCESS ('192.168.1.154', 63581) /www/index.html
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63582)
    2000-01-02T09:36:59.006 [info] esp8266: ACCESS ('192.168.1.154', 63582) /www/foo
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63583)
    2000-01-02T09:36:59.006 [info] esp8266: ACCESS ('192.168.1.154', 63583) /www/index.html
    2000-01-02T09:36:59.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63590)
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63591)
    2000-01-02T09:37:00.006 [info] esp8266: ACCESS ('192.168.1.154', 63591) /www/foo/bar/test.js
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63592)
    2000-01-02T09:37:00.006 [info] esp8266: ACCESS ('192.168.1.154', 63592) /www/foo/bar/test.css
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63593)
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63596)
    2000-01-02T09:37:00.006 [info] esp8266: NOT_FOUND ('192.168.1.154', 63596) /www/bar
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63597)
    2000-01-02T09:37:00.006 [info] esp8266: FORBIDDEN ('192.168.1.154', 63597) /..
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63598)
    2000-01-02T09:37:00.006 [info] esp8266: ACCESS ('192.168.1.154', 63598) /www/foo/test.txt
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63599)
    2000-01-02T09:37:00.006 [info] esp8266: ACCESS ('192.168.1.154', 63599) /www/foo/test.txt
    2000-01-02T09:37:00.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63600)
    2000-01-02T09:37:00.006 [info] esp8266: ACCESS ('192.168.1.154', 63600) /www/foo/test.txt
    2000-01-02T09:37:01.006 [info] esp8266: AUTHORIZED ('192.168.1.154', 63601)
    2000-01-02T09:37:01.006 [info] esp8266: ACCESS ('192.168.1.154', 63601) /www/foo/bar
