
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

Start by creating a 

    >>> import os
    >>> os.mkdir('/www')
    >>> os.mkdir('/www/js')
    >>> os.mkdir('/www/js/lib')




# Architecture
