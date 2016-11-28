# Micropython HTTP daemon

This set of modules provides a simple HTTP framework and daemon, for providing an HTTP interface into your ESP8266.

By itself, the `uhttpd` module is just a server and framework for adding handlers to process HTTP requests.  This directory contains one handler, for serving files stored in the micropython file system

> Warning: This software provides _no security_ for your applications.  When this software is running, any machine on your network may connect to your ESP8266 and browse the parts of the file system you expose through configuration, including possibly senstive security credentials stored in plain text.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED IN A PRODUCTION ENVIRONMENT OR IN AN UNTRUSTED NETWORK!


## Modules and Dependencies

The `uhttpd` framework and server is comprised the following python modules:

* `uhttpd.py` -- provides HTTP server and framework
* `utcp_server.py` -- provides basic TCP networking layer of abstraction
* `http_file_handler.py` -- a file handler for the `uhttpd` server

This module relies on the `ulog.py` facility, defined in the [logging](/micropython/logging) area of this repository.

## Basic Usage

Start by creating a directory (e.g., `www`) on your file system in which you can place HTML (or other) files:

    >>> import os
    >>> os.mkdir('www')
    >>> os.chdir('www')
    >>> f = open('index.html', 'w')
    >>> f.write('<html><body>Hello World!</body></html>')
    38
    >>> f.close()
    >>> os.listdir()
    ['index.html']

To run the `uhttpd` server, initialize an instance of the `uhttpd.Server` class with an ordered list of tuples, which map URL prefixes to handlers, and start the server.

For example, to start the server with the file handler keyed off the `/www` path, use the following: 

    >>> import uhttpd
    >>> import http_file_handler
    >>> server = uhttpd.Server([('/www', http_file_handler.Handler())])
    >>> server.start()

You should then see some logs printed to the console, like:

    2000-01-01T05:08:09.005 [info]: TCP server started on 192.168.4.1:80
    2000-01-01T05:08:09.005 [info]: TCP server started on 192.168.1.180:80

You may now connect to your ESP8266 via a web browser or curl and browse your file system, e.g.,

    prompt$ curl -i 'http://192.168.1.180/www' 
    HTTP/1.1 200 OK
    Content-Length: 38
    Content-Type: text/html
    
    <html><body>Hello World!</body></html>


## The HTTP File Handler

As noted above, this software includes a request handler (`http_file_handler.py`) for servicing files on the ESP8266 file system.

This handler will display the contents of the directory specified in the HTTP GET URL as an HTML page with hyperlinks to files and subdirectories.  If a file exists in the directory with the name `index.html`, this file will be loaded, instead.

This handler only support HTTP GET requests.  Any other request will be rejected.

> TODO: Future versions of this handler may support configuration to allow better protection of the file and directory contents, in the spirit of Apache httpd.

## TODO

Document the handler mechanism and techniques for implementing REST-ful APIs.
