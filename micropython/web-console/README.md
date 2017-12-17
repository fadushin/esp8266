
# Overview

Web Console is a proof-of-concept web application for managing an ESP8266 running Micropython.  The application is useful in its own right for connecting, controlling, and monitoring an ESP8266 device, but it may also be used as a basis for applications you may write for this platform.  It is mostly provided as an exercise to flush out the Micropython `uhttpd` server and APIs, while also providing a working example from which to develop more sophisticated applications.

Web Console makes use of the `uhttpd` web server.  A `uhttpd.Server` instance is created and started on the ESP8266, which services a collection of HTML, Javascript, and CSS files.  In addition, the `uhttpd.Server` is instantiated with a collection of API handlers, for servicing REST-ful APIs for managing the ESP8266 device.  The Javascript files that are part of the application make use of these APIs for read and write operations on the ESP8266.

This web application makes use of several open source Javascript and CSS modules, which provide a client-side MVC framework which runs in the web browser.  The Rest-ful APIs are deliberately simple and are designed to have minimal impact on the ESP8266 device, itself.  Instead, the rendering of HTML and logic governing presentation of panels, controls, dialog boxes, and so forth, is all managed from code running in the web browser.

## License

The source modules that form the Web Console application are distributed under a modified BEER-WARE License:

    # ----------------------------------------------------------------------------
    # "THE BEER-WARE LICENSE" (Revision 42):
    # <fred@dushin.net> wrote this file.  You are hereby granted permission to
    # copy, modify, or mutilate this file without restriction.  If you create a
    # work derived from this file, you may optionally include a copy of this notice,
    # for which I would be most grateful, but you are not required to do so.
    # If we meet some day, and you think this stuff is worth it, you can buy me a
    # beer in return.   Fred Dushin
    # ----------------------------------------------------------------------------

# Installation

These instructions assume you have built and installed the `uhttpd` application on your device.  Note that for the esp8266, you will need to burn the uhttpd modules (including the file and api handlers, logging and uasyncio dependencies) as frozen bytecode into your device.  There simply is not enough memory on these devices to run this application off the python vFat file system.

Start by creating a directory tree on your device that contains a `/www`, `/www/js`, and `/www/js/lib` directory:

    >>> import os
    >>> os.mkdir('/www')
    >>> os.mkdir('/www/js')
    >>> os.mkdir('/www/js/lib')

Upload the files in the `www` directory to your device in their corresponding locations on the device.  For example:

    prompt$ IP_ADDRESS = # enter the IP address of your device
    prompt$ cd .../esp8266/micropython/web-console
    prompt$ for i in $(find www -type f); do webrepl_cli.py $i ${IP_ADDRESS}:/$i; done
    ...


Updload the `api.mpy` to your device, preferably as frozen bytecode burned into your image, but alternatively in the `/` or `/lib` directory of your device.

You may now run the HTTP server, as follows:

    def web_console():
        import uhttpd
        import uhttpd.file_handler
        import uhttpd.api_handler
        import api

        api_handler = uhttpd.api_handler.Handler([
            (['system'], api.SystemAPIHandler()),
            (['memory'], api.MemoryAPIHandler()),
            (['flash'], api.FlashAPIHandler()),
            (['network'], api.NetworkAPIHandler())
        ])
        file_handler = uhttpd.file_handler.Handler()
        server = uhttpd.Server([
            ('/api', api_handler),
            ('/', file_handler)
        ], {'max_headers': 50, 'backlog': 10})
        server.run()

For example:

    >>> web_console()
    loaded sink console
    2000-01-01T05:55:49.005 [info] esp8266: uhttpd-master running...

You may now connect to your device over a web browser, e.g.,

http://192.168.1.174/

The application should load into your browser, and after a short load period, should give you a menu of information about your device, such as system information, memory and disk usage, network status, etc.  For example,

![Web Console](/micropython/web-console/images/memory-screenshot.png)

# Architecture

TODO
