# Micropython HTTP daemon

This set of modules provides a simple HTTP framework and daemon, for providing an HTTP interface into your ESP8266.

By itself, the `uhttpd` module is just a server and framework for adding handlers to process HTTP requests.  This directory contains one handler, for serving files stored in the micropython file system

> Warning: This software provide _no security_ for your applications.  When this software is running, any machine on your network may connect to your ESP8266 and browse the contents of your file system, including possibly senstive security credentials stored in plain text.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED FOR PRODUCTION USE!!


## Dependencies

This module relies on the `ulog.py` module in the common area of this repository.

## Usage

To run the `uttpd` server, initialize an instance of the `uttpd.Server` class with an ordered list of tupes, which map URL prefixes to handlers, and start the server.

For example, to start the server with the file handler keyed off the root path, use the following: 

    import uhttpd
    import http_file_handler
    
    server = uhttpd.Server([('/', http_file_handler.Handler())])
    server.start()

You should then see some logs printed to the console, like:

    2000-01-01T05:08:09.005 [info]: TCP server started on 192.168.4.1:80
    2000-01-01T05:08:09.005 [info]: TCP server started on 192.168.1.180:80

You may now connect to your ESP8266 via a web browser or curl and browse your file system, e.g.,

    prompt$ curl -i 'http://192.168.1.180/' 
    HTTP/1.1 200 OK
    Content-Length: 321
    Content-Type: text/html

    <html><body><a href="/boot.py">boot.py</a><br>
    <a href="/webrepl_cfg.py">webrepl_cfg.py</a><br>
    <a href="/utcp_server.py">utcp_server.py</a><br>
    <a href="/ulog.py">ulog.py</a><br>
    <a href="/http_file_handler.py">http_file_handler.py</a><br>
    <a href="/uhttpd.py">uhttpd.py</a><br>
    <a href="/lib">lib</a><br>
    </body></html>


## The HTTP File Handler

As noted above, this software includes a request handler (`http_file_handler.py`) for servicing files on the ESP8266 file system.

This handler will display the contents of the directory specified in the HTTP GET URL as an HTML page with hyperlinks to files and subdirectories.  If a file exists in the directory with the name `index.html`, this file will be loaded, instead.

This handler only support HTTP GET requests.  Any other request will be rejected.

> TODO: Future versions of this handler may support configuration to allow better protection of the file and directory contents, in the spirit of Apache httpd.

## TODO

Document the handler mechanism and techniques for implementing REST-ful APIs.
