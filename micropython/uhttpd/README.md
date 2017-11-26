# Micropython HTTP daemon

This set of modules provides a simple HTTP framework and server, providing an HTTP interface into your ESP8266.  Having an HTTP server allows developers to create management consoles for their ESP8266 devices, which can be very useful for configuration and troubleshooting devices, or even for bootstrapping them from an initial state.

Features include:

* Support for a subset of the HTTP/1.1 protocol (RFC 2616)
* Asynchronous handling of requests, so that the server can run while the ESP8266 runs other tasks
* Support for HTTP/Basic authentication
* Handler for servicing files on the Micropython file system
* Extensible API for adding REST-ful JSON and query-based APIs


By itself, the `uhttpd` module is just a TCP server and framework for adding handlers to process HTTP requests.  The actual servicing of HTTP requests is done by installing HTTP Request handlers, which are passed to the `uhttpd` server at creation time.  It's the Request Handlers that actually do the heavy lifting when it comes to servicing HTTP requests.  Request Handlers are triggered based on the URLs that are used by the client.  Multiple Request Handlers can be installed, each of which can handle a special case based on a particular URL prefix.

This package includes a Request Handler for servicing files on the micropython file system (e.g., HTML, Javascript, CSS, etc), as well as a Request Handler for managing REST-ful API calls, essential components in any modern web-based application.  The API Request Handler in turn supports the addition of application-specific API Handlers, described in more detail below.

Once started, the `uhttpd` server runs in the background, so that the ESP8266 can do other tasks.  When the server accepts a request, however, the ESP8266 will block for the period of time it takes to process the request, i.e., read and parse the request sent from the client, dispatch the parsed request to the designated handler to get a response, and send the response back to the client.  Ordinarily, this should only take a few milliseconds, but applications may vary in their request processing time.

TCP/IP connections between clients and the `uhttpd` server endure for the duration of a single request.  Once the client opens a connection to the server, the server will dispatch the request to an appropriate handler and wait for the response from the handler.  It will then send the response back to the client on the open connection, and then close the connection to the client.
 
A driving design goal of this package is to have minimal impact on the ESP8266 device, itself, and to provide the tools that allow developers to implement rich client-side applications.  By design, web applications built with this framework should do as little work as possible on the server side, but should instead make use of modern web technologies to allow the web client or browser to perform significant parts of business logic.  In most cases, the web clients will have far more memory and compute resources than the ESP8266 device, itself, so it is wise to keep as much logic as possible on the client side.

## Limitations

While the `uhttpd` code is intended to be a robust HTTP server for many needs, there are currently some limitations users should be aware of:

* There are currently limitations to the number of concurrent requests made on the server.  Many web browsers will attempt to run multiple connections to a given host, and will attemt to load resources (images, scripts, stylesheets, etc) in parallel.  The current implementation is unable to service requests in parallel, and many of the connections the web browser makes will get dropped, resulting in delays or inability to load page content.  You *might* be able to work around these limitations by in-lining as many of your scripts and resources as possible.  Work is ongoing to address this limitation.
* This software currently does not support SSL, and therefore provides no transport-layer protection for your applications.  When this software is running, requests are sent in clear text, including not only the HTTP headers you may use for authentication, but also the contents of the HTTP requests and responses.  Malicious users on your network using off-the-shelf packet sniffers can read your HTTP traffic with no difficulty.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED FOR USE IN AN UNTRUSTED NETWORK!
* The amount of workable RAM is very limited on the ESP8266, on the order of 32kb.  Users should design applications with this in mind.

## Modules and Dependencies

The `uhttpd` framework and server is comprised the following python package:

* `uhttpd/`
	* `uhttpd.py` -- provides HTTP server and framework
	* `file_handler.py` -- a file handler for the `uhttpd` server
	* `api_handler.py` -- a handler for servicing REST-ful APIs

This package relies on the `logging` facility, defined in [logging](https://github.com/micropython/micropython-lib/tree/master/logging).

There is currently no `upip` support for this package.

## Loading Modules

Some of the modules in this package require significant amounts of RAM to load and run.  While you may be able to run some combination of these modules by loading them on the Micropython file system and allowing the runtime to compile the source modules for you, you will likely run out of RAM before you hit more than a trivial example.  It is therefore recommended to either freeze the modules in your firmware (recommended) or to compile to bytcode and load the generated `.mpy` files, which will decrease the memory footprint of your application using these modules.

Both frozen and pre-compiled bytecode require building the [micropython](https://github.com/micropython/micropython/tree/master/esp8266) project.  


### Frozen Bytecode (recommended)

For production applications, it is recommended to freeze the `uhttpd` bytecode to your firmware image.  The step-by-step details for building micropython firmware images are outside of the scope of this document, but essentially, all you need to do is:

* Copy (or symlink) the following third-party dependencies from the [micropython-lib](https://github.com/micropython/micropython-lib) repository:
    * [uasyncio.core](https://github.com/micropython/micropython-lib/tree/master/uasyncio.core)
    * [uasyncio](https://github.com/micropython/micropython-lib/tree/master/uasyncio)
    * [logging](https://github.com/micropython/micropython-lib/tree/master/logging)
* Copy (or symlink) the `uhttpd` python modules to the `modules` directory of your `micropython/esp8266` directory
* Build and deploy your firmware image as described in the [micropython](https://github.com/micropython/micropython/tree/master/esp8266) instructions

Your modules directory should contains the following links (or copies), where `${THIS_REPO}` is your local working copy of this repository, and `${ML_REPO}` is your local working copy of the [micropython-lib](https://github.com/micropython/micropython-lib) repository

    uhttpd/__init__.py@ -> ${THIS_REPO}/micropython/uhttpd/uhttpd/__init__.py
    uhttpd/api_handler.py@ -> ${THIS_REPO}/micropython/uhttpd/uhttpd/api_handler.py
    uhttpd/file_handler.py@ -> ${THIS_REPO}/micropython/uhttpd/uhttpd/file_handler.py
    logging.py@ -> ${ML_REPO}/logging/logging.py

In addition, make a directory called `uasyncio` under modules directory with symlinks to (or copies of) the `uasyncio` and `uasyncio.core` libraries in the micrpython-lib repository:

    uasyncio/__init__.py@ -> ${ML_REPO}/uasyncio/uasyncio/__init__.py
    uasyncio/core.py@ -> ${ML_REPO}/uasyncio.core/uasyncio/core.py

### Pre-compiled modules

If you are doing any development on the `uhttpd` source code, you can upload modifications to the source code module to the micropython file system.  Note, however, that there is limited RAM resources on a typical ESP8266 device, and in general you will not be able to do much testing on modules that are loaded and compiled on the micropython runtime.  You can reduce RAM usage by pre-compiling modules using the `mpy-cross` compiler, included in the [micropython](https://github.com/micropython/micropython/tree/master/esp8266) repository, but even then, you will be very limited in what you can get to run in such a tightly constrained environment.  For these reasons, we recommend using frozen bytecode, even for resting changes to these modules.

> Note.  You cannot replace modules that are already burned into a micropython image.  If you want to upload a python module, compiled or otherwise, that is already frozen in the image, you will need to flash an image without the modules you are going to upload.

If you want to try uploading pre-compiled modules, you will need to have the `mpy-cross` tool built and in your PATH environment variable.  You can then use the supplied `Makefile` to generate `.mpy` files.  Loading the generated bytecode files, instead of the python files, will reduce memory overhead during the development process of your application.

For example, to build the bytecode, 

    prompt$ export PATH=/Volumes/case-sensitive/micropython/mpy-cross:$PATH
    prompt$ pwd
    /work/src/github/fadushin/esp8266/micropython
    prompt$ make
	mpy-cross -o build/mpy/logging/ulog.mpy logging/ulog.py
	mpy-cross -o build/mpy/logging/console_sink.mpy logging/console_sink.py
	mpy-cross -o build/mpy/logging/syslog_sink.mpy logging/syslog_sink.py
	mpy-cross -o build/mpy/uhttpd/uhttpd/__init__.mpy uhttpd/uhttpd/__init__.py
	mpy-cross -o build/mpy/uhttpd/uhttpd/file_handler.mpy uhttpd/uhttpd/file_handler.py
	mpy-cross -o build/mpy/uhttpd/uhttpd/api_handler.mpy uhttpd/uhttpd/api_handler.py
	mpy-cross -o build/mpy/uhttpd/demo/stats_api.mpy uhttpd/demo/stats_api.py
	mpy-cross -o build/mpy/uhttpd/demo/my_api.mpy uhttpd/demo/my_api.py
	mpy-cross -o build/mpy/tools/ush.mpy tools/ush.py
	mpy-cross -o build/mpy/uhttpd/test/test_server.mpy uhttpd/test/test_server.py
	mpy-cross -o build/mpy/web-console/api.mpy web-console/api.py

If you have `webrepl` running and `webrepl_cli.py` in your `PATH`, then you can upload the files you need to your device (adjusted of course for the IP address of your ESP8266), as needed.  Instructions for using `webrepl_cli.py` are outside of the scope of this document.

> Note. You can fine simple shell scripts for uploading and downloading files using the `webrepl_cli.py` script in the `bin` directory.

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

To run the `uhttpd` server, initialize an instance of the `uhttpd.Server` class with an ordered list of tuples, which map URL prefixes to handlers, and start the server.  When creating a HTTP file handler, you can optionally specify the "root" of the file system from which to serve files. 

For example, to start the server with the file handler rooted off the `/www` path, use the following: 

    >>> import uhttpd
    >>> import uhttpd.file_handler
    >>> server = uhttpd.Server([('/', uhttpd.file_handler.Handler('/www'))])
    >>> server.run()

The above sequence of statements will start the `uhttp` server, listening on port 80.  Any HTTP requests beginning with the URL prefix '/' (viz., all requests) will be routed to the `uhttpd.file_handler.Handler`, which will service files on the micropython file system under the directory `/www`.  Attempts to read data outside of this path will fail with a 403 (forbidden) exception.

Once the `uhttpd.Server` is started, you should then see some logs printed to the console, indicating that the server is listening for connections:

    2016-12-18T09:57:46.005 [info] esp8266: uhttpd-master started.

You may now connect to your ESP8266 via a web browser or curl and browse your file system, e.g.,

    prompt$ curl -i 'http://192.168.1.180/' 
    HTTP/1.1 200 OK
    Server: uhttpd/master (running in your devices)
    Content-Length: 38
    Content-Type: text/html
    
    <html><body>Hello World!</body></html>

## HTTP Authentication

The `uhttpd.Server` supports HTTP Basic authentication.  By default, HTTP authentication is not required, but you can configure the `uhttpd.Server` to require authentication by setting the `require_auth` configuration property to `True` in the `uhttpd.Server` constructor.  (For more information about the `uhttpd.Server` constructor, see the _Configuration_ section below.)

    >>> import uhttpd
    >>> import uhttpd.file_handler
    >>> server = uhttpd.Server(
        [('/', uhttpd.file_handler.Handler('/www'))],
        config={'require_auth': True}
    )
    >>> server.run()

The default HTTP user name is `admin`, and the default password is `uhttpD`, but these values are configurable, as described in the _Configuration_ section, below.  This server only supports one username and password for each server instance.

> Warning: This software currently provides no transport-layer protection for your applications.  HTTP credentials, while obfuscated with BASE-64 encoding, per the HTTP 1.1 spec, are sent in plaintext, and are therefore accessible to malicious parties on your network.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED FOR USE IN AN UNTRUSTED NETWORK!

If you try to make a request without supplying HTTP Basic authentiction credentials (i.e., a username and password), your request will be rejected with an HTTP 401 error:

    prompt$ curl -i 'http://192.168.1.180' 
    HTTP/1.1 401 Unauthorized
    Server: uhttpd/master (running in your devices)
    Content-Type: text/html
    www-authenticate: Basic realm=esp8266
    
    <html><body><header>uhttpd/master<hr></header>Unauthorized</body></html>

If you use a web browser to access this page, you should get a popup window prompting you for a username and password.

When you supply the correct credentials (e.g., via `curl`), you should be granted access to the requested URL:

    prompt$ curl -i -u admin:uhttpD 'http://192.168.1.180' 
    HTTP/1.1 200 OK
    Server: uhttpd/master (running in your devices)
    Content-Length: 40
    Content-Type: text/html
    
    <html><body>Hello World!</body></html>

## HTTP File Handler

This package includes a Request Handler, `uhttpd.file_handler.Handler` which when installed will service files on the ESP8266 file system, relative to a specified file system root path (e.g., `/www`).

> Note.  The `uhttpd` modules have recently been reorganized into a python package.  The old `http_file_handler` module is still available and can be used as before, but users will get a warning on the console when the module is loaded.  Develoeprs should replace uses of `http_file_handler` with `uhttpd.file_handler` at their earliest convenience.

This Request Handler will display the contents of the path specified in the HTTP GET URL, relative to the specified root path.  If path refers to a file on the file system, the file contents are returned.  If the path refers to a directory, and the directory does not contain an `index.html` file, the directory contents are provided as a list of hyperlinks.  Otherwise, the request will result in a 404/Not Found HTTP error.  If a request is made on a path outside of the specified root path, then request will fail with a 403 Forbidden error.

The default root path for the `uhttpd.file_handler.Handler` is `/www`.  For example, the following constructor will result in a file handler that services files in and below the `/www` directory of the micropython file system:

    >>> import uhttpd.file_handler
    >>> file_handler = uhttpd.file_handler.Handler()

Once your handler is created, you can then provide it to the `uhttpd.Server` constructor, providing the path prefix used to locate the handler at request time:

    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/', file_handler)
        ])

> Important: The path prefix provided to the `uhttpd.Server` constructor is distinct from the root path provided to the `uhttpd.file_handler.Handler` constructor.  The former relates to the path specified in a given HTTP GET request and is used to pick out the handler to process the handler.  The latter is used to locate where, on the file system, to start looking for files and directories to serve.  If the root path is `/www` and the path in the HTTP request is `/foo/bar`, then the `uhttpd.file_handler.Handler` will look for `/www/foo/bar` on the micropython file system.

You may of course specify a root path other than `/www` through the `uhttpd.file_handler.Handler` constructor, but the directory must exist, or an error will occur at the time of construction. 

> Warning: If you specify the micropython file system root path (`/`) in the HTTP File Handler constructor, you may expose sensitive security information, such as the Webrepl password, through the HTTP interface.  This behavior is strongly discouraged.

You may optionally specify the `block_size` as a parameter to the `uhttpd.file_handler.Handler` constructor.  This integer value (default: 1024) determines the size of the buffer to use when streaming a file back to the client.  Larger chunk sizes require more memory and may run into issues with memory.  Smaller chunk sizes may result in degradation in performance.  If a memory error occurs when creating this buffer, the file handler will attempt to allocate buffer one half the size of the previous failed allocation, until either the allocation succeeds, or not even a single byte buffer is available.

This handler only supports HTTP GET requests.  Any other HTTP request verb will be rejected.

This handler recognizes HTML (`text/html`), CSS (`text/css`), and Javascript (`text/javascript`) file endings, and will set the `content-type` header in the response, accordingly.  The `content-length` header will contain the length of the body.  Any file other than the above list of types is treated as `text/plain`

## API Handlers

The `uhttpd` server can be extended by implementing and instantiating API Handlers passed to the `uhttpd.api_handler.Handler` class constructor, an HTTP Request Handler.  Doing so allows you to write REST-based APIs that allow your application to respond to application protocols of your own design.  For example, an application may need to control endpoints to which the embedded device communicates, and such configuration might be managed through a web console, which in turn might use a REST-based API to read and write configuration entries for the application.

> Note.  The `uhttpd` modules have recently been reorganized into a python package.  The old `http_api_handler` module is still available and can be used as before, but users will get a warning on the console when the module is loaded.  Develoeprs should replace uses of `http_api_handler` with `uhttpd.api_handler` at their earliest convenience.

Messages and be sent to handlers via a combination of URLs, including query string parameters, as well as JSON or raw byte array messages in the body of an HTTP request and response.  Standard HTTP verbs, including "get", "put", "post", and "delete" are supported.  The underlying `uhttpd.api_handler.Handler` class manages the transformation of data from and to the `uhttpd.Server` class, so you can focus on the business needs of your application, and not on the details of the HTTP protocol.

To implement an API Handler, all you need to do is define a class which implements one or more of the following operations:

* `get(self, api_request)`
* `put(self, api_request)`
* `post(self, api_request)`
* `delete(self, api_request)`

The inputs, return values, and exception semantics for these operstions are defined in more detail below, but the basic idea is, "query parameters and JSON in, JSON out", but there are exceptions to this rule, if neeeded.

You do not need to implement _all_ of these operations; only the operations your application needs to respond to.  If a client makes a request on an API Handler for an operation that is not defined, they will receive a bad request error (HTTP 400).

The function names correspond in a predictable way to the corresponding verbs that define the HTTP protocol.  For example, if the HTTP request is a "GET" request, then the `get` function will be called on the corresponding handler.  Similarly for "PUT", "POST", and "DELETE".

> Note.  Not all HTTP verbs are currently supported.

### Example

To install an API Handler, provide an instance of it to the `uhttpd.api_handler.Handler` constructor, which in turn is installed into the `uhttpd.Server`.  For example, if your API handler is called `Handler` and is defined in the `my_api.py` module:

    # my_api.py
    class Handler:
        def __init__(self):
            pass
        
        def get(self, api_request):
            return {'foo': 'bar'}

then you can install the API Handler as follows:

    >>> import my_api
    >>> import uhttpd.api_handler
    >>> api_handler = uhttpd.api_handler.Handler([(['test'], my_api.Handler())])
    >>> import uhttpd
    >>> server = uhttpd.Server([('/api', api_handler)])
    >>> server.run()
    2016-12-18T10:24:33.005 [info] esp8266: uhttpd-master started.

You can then make HTTP requests to your handler via:

    prompt$ curl -i 'http://192.168.1.180/api/test
    HTTP/1.1 200 OK
    Server: uhttpd/master (running in your devices)
    content-type: application/json
    content-length: 14
    
    {"foo": "bar"}

### Inputs

The API handler method all take a single `api_request` parameter, which encapsulates the data present in the current request.  This parameter is a dictionary containing elements that have been parsed off the HTTP request and TCP/IP connection.  In many cases, applications do not need to deeply inspect the contents of this object, but portions of its structure are needed for handling common requests.

The entries of an API request structure include the following keys:

* `'prefix'` The prefix used to identify the API handler.  For example, if the API handler is registered with the `uhttpd.api_handler.Hander` using the prefix ['demo'], then the `'prefix'` value will be `['demo']`.
* `'context'`  This entry contains a list of path components in the HTTP request after the prefix.  For example, if the API handler is registered with the `uhttpd.api_handler.Hander` using the prefix ['demo'], and the `uhttpd.api_handler.Handler` is registered with the `uhttpd.Server` class with the prefix `/api`, when the HTTP request is `/api/demo/foo/bar`, the `'context'` entry will contain the list `['foo', 'bar']`.
* `'query_params'`  This entry contains a dictionary containing any query parameters that were delivered with the request, as a set of name-value pairs.  For example, if the HTTP request contains the path `/api/demo?foo=bar`, then the `'query_params'` entry will contain the dictionary `{'foo': "bar"}`.  The value of each query parameter is always of type string.
* `'body'`  The body of the request as a parsed JSON structure, if it has been passed as JSON, and if the content type defined in the HTTP request is `application/json`.  Otherwise, this parameter is not defined.  See the `'http'` element for the raw bytes containing the HTTP body, if it has been provided.
* `'http'`  This entry contains a dictionary containing elements parsed off the HTTP request.  More details of this object are described below.

The `http` entry contains a dictionary of elements that have been parsed off the HTTP request.

* `'verb'` The HTTP "verb" (e.g., "get", "put", "post", etc.)  The string value provided on the wire is converted to lower case.
* `'path'`  The path, as it was specified in the HTTP request
* `'protocol'` The HTTP protocol provided by the client (e.g., "HTTP/1.1")
* `'prefix'`  This entry dentotes the prefix with which the HTTP Request Handler was registered with the `uhttpd.Server`.
* `'headers'` A dictionary containing the HTTP headers parsed from the HTTP request.  All keys in this dictionary are lower case.
* `'user'` If HTTP authentication is required and the user has successfully authenticated, this entry contains the user name supplied via HTTP authentication headers.  Otherwise, this entry is not present in the `http` dictionary.
* `'body'`  The body of the request, as a byte array.  If no body is present in the request, then this entry is not defined.
* `'tcp'` A dictionary containing properties of the client TCP/IP connection.

The `tcp` entry contains the following elements:

* `'remote_addr'` The remote address of the HTTP client

### Return value

The return value from these operations may one of the following:

* A JSON structure (i.e., python Dictionary) that can be converted to a JSON string:  In this case, the body of the HTTP response is the converted JSON string, and the content type is set to `application/json`.
* A raw byte array:  In this case, the raw byte array is returned in the body of the HTTP response, and the content type is set to `application/binary`.
* A string: In this case, the string is returned as a body of HTTP response. Content-type is set to `text/html; charset=utf-8`
* `None`: In this case, the HTTP response contains no body.

### Exception Semantics

Handlers will generally return a JSON structure representing a response.  If, however, an error occurs in processing a request, the Handler may raise an exception, which will get processed by the underlying HTTP server, and an appropriate reponse code will be returned to the caller.

Raising the following exceptions will generate the corresponding error codes back to the client:

* `uhttpd.BadRequestException`: 400
* `uhttpd.NotFoundException`: 404
* `uhttpd.ForbiddenException`: 403

Any other exception extending `BaseException` will generate an internal server error (500)


## Reference

The following sections describe the components that form the `uhttpd` package in more detail.

### `uhttpd.Server`

The `uhttpd.Server` is a container for HTTP Request Handlers.  Its only job is to accept connections from clients, to read and parse HTTP headers, to enforce HTTP authentication, if so configured, and to read the body of the request, if present.  The server will the dispatch the request to the first handler that matches the path indicated in the HTTP request, and wait for a response.  Once received, the response will be sent back to the caller.

An instance of a `uhttpd.Server` is created using an ordered list of pairs, where the first element of the pair is a path prefix, and the second is a handler instance.  When an HTTP request is processed, the server will select the handler that corresponds with the first path prefix which is a prefix of the path in the HTTP request.

For example, given the following construction:

    >>> import uhttpd
    >>> handler1 = ...
    >>> handler2 = ...
    >>> handler3 = ...
    >>> server = uhttpd.Server([
            ('/foo/', handler1),
            ('/gnu', handler2),
            ('/', handler3)
        ])
    >>> server.run()

a request of the form `http://host/foo/bar/` will be handled by `handler1`, whereas a request of the form `http://host/gnat/` will be handled by `handler3`.

Once started, the `uhttpd.Server` will listen asynchronously for connections.  While a connection is not being serviced, the application may proceed to do work (e.g., via the REPL).  Once a request is accepted, the entire request processing, including the time spent in the handlers, is synchronous.

A `uhttpd.Server` may be stopped via the `stop` method.

#### Configuration

The `uhttpd.Server` can be configured using the `config` parameter at construction time, which is dictionary of name-value pairs.  E.g.,

    server = uhttpd.Server([...], config={'port': 8080})

The valid entries for this configuration parameter are described in detail below.

##### `bind_addr`

This parameter denotes the network interface on which the `uhttpd` should listen.  The type of this paramter is `string`, and the default value is `0.0.0.0`, meaning all interfaces.

##### `port`

This parameter denotes the TCP/IP port on which the `uhttpd` should listen.  The type of this paramter is `int`, and the default value is 80.

##### `timeout`

This parameter denotes the maximum timeout on a connection before a connection is closed.  The type of this paramter is `int` and the units are indicated in seconds.  The default value is 30 (seconds).

##### `require_auth`

This parameter indicates whether HTTP authentication is required.  The type of this parameter is boolean, and the default value is `False`.  If this parameter is set to `True`, all requests into this server instance require HTTP authentication headers, per RFC 7231.

##### `realm`

This parameter denotes the HTTP authorization realm in which users should be authenticated.  This realm is returned back to the HTTP client when authorization is required but not credentials are supported.  The type of this parameter is `string`.  The default realm is `esp8266`.

##### `user`

This parameter denotes the HTTP user name, which needs to be supplied by the user in an HTTP Basic authentication header, per RFC 7231.  The default user name is `admin`.

##### `password`

This parameter denotes the HTTP password, which needs to be supplied by the user in an HTTP Basic authentication header, per RFC 7231.  The default password is `uhttpD`.

##### `max_headers`

This parameter denotes the maximum number of headers an HTTP request may contain.  If a request exceeds this maximum, the request will fail with an HTTP 400 Bad Request error.  The default value is 25.

##### `max_content_length`

This parameter denotes the maximum size (in bytes) of the body of an HTTP request.  If a request exceeds this maximum, the request will fail with an HTTP 400 Bad Request error.  The default value is 1024.

### `uhttpd.file_handler.Handler`

> Note.  The `uhttpd` modules have recently been reorganized into a python package.  The old `http_file_handler` module is still available and can be used as before, but users will get a warning on the console when the module is loaded.  Develoeprs should replace uses of `http_file_handler` with `uhttpd.file_handler` at their earliest convenience.

The `uhttpd.file_handler.Handler` request handler is designed to service files on the ESP8266 file system, relative to a specified file system root path (e.g., `/www`).

This class supports the following properties at initialization:

* `root_path`  (default: `"/www"`)  The root path from which to serve files.
* `block_size`  (defualt: `1024`)  The size of the buffer used to stream files back to the client.  If a memory error occurs when creating this buffer, the file handler will attempt to allocate buffer one half the size of the previous failed allocation, until either the allocation succeeds, or not even a single byte buffer is available.

> Warning.  You should set `root_path` to a directory that does not contain sensitive security information, such as usernames or passwords used to access the device or for the device to reach external services.

    >>> import uhttpd.file_handler
    >>> file_handler = uhttpd.file_handler.Handler(root_path='/www', blcok_size=128)

Once your handler is created, you can then provide it to the `uhttpd.Server` constructor, providing the path prefix used to locate the handler at request time:

    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/', file_handler)
        ])

Typically, the HTTP File Handler should be defined last in the list of Request Handlers, with '/' as the first element of the tuple.  That way, specialized API handlers can get called based on paths known to your application (e.g., `/api`) and will not get serviced by the HTTP File handler.  To the contrary, the HTTP File handler can service HTML, CSS, and Javascript files, some of which may end up calling APIs in your application.

### `uhttpd.api_handler.Handler`

> Note.  The `uhttpd` modules have recently been reorganized into a python package.  The old `http_api_handler` module is still available and can be used as before, but users will get a warning on the console when the module is loaded.  Develoeprs should replace uses of `http_api_handler` with `uhttpd.api_handler` at their earliest convenience.

The `uhttpd.api_handler.Handler` request handler is designed to handle REST-ful API calls into the `uhttpd` server.  Currently, JSON is the only supported message binding for REST-ful API calls through this handler.

This handler should be initialized with an ordered list of tuples, mapping a list of API "components" to an API handler instance, which will be used to actually service the API request.  A component, in this sense, is a sequence of path elements

    >>> import uhttpd.api_handler
    >>> api1 = ...
    >>> api2 = ...
    >>> api3 = ...
    >>> api_handler = uhttpd.api_handler.Handler([
            (['foo'], api1),
            (['gnu'], api2),
            ([], api3),
       ])

You can then add the API handler to the `uhttpd.Server`, as we did above with the HTTP File Handler:

    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/api', api_handler),
            ('/', file_handler)
        ])

This way, any HTTP requests under `http://host/api` get directed to the HTTP API Handler, and everything else gets directed to the HTTP File Handler.

The HTTP API Handler, like the `uhttp.Server`, does not do much processing on the request, but instead uses the HTTP path to locate the first API Handler that matches the sequence of components provided in the constructor.  In the above example, a request to `http://host/api/foo/` would get processed by the `api1` handler (as would requests to `http://host/api/foo/bar`), whereas requests simply to `http://host/api/` would get procecced by the `api3` handler.

For more information about API Handlers, see the _Writing API Handlers_ section.
