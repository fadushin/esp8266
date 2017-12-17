# `ulog` Facility

The `ulog` facility provides basic logging operations for micropython applications.  

This facility provides a simple logging API for applications, which is suitable for most applications.  The facility provides a default logger, which is initialized when the `ulog` module is imported, and can be used out of the box for console logging applciations.  The default logger may be optionally configured via a configuration file, which can be placed on the python path to alter the default behavior of this logger.  Advanced users may create additional logger instances, each with their own configuration.

This facility supports numerous log "sinks", to which log messages may be redirected.  The currently supported log sinks are to the console and to a syslog server running on the network and accepting UDP syslog packets per RFC 5424 (e.g., via `rsyslogd`).

## Modules and Dependencies

The `ulog` facility is comprised the following python modules:

* `ulog.py` -- provides core logging APIs
* `console_sink.py` -- log sink for printing log messages to the console (not required for advanced usage)
* (optional) `log_config.py` -- Optional configuration for the default logger
* (optional) `syslog_sink.py` -- log sink for directing log messages to a syslog server on your network (requires https://github.com/kfricke/micropython-usyslog/blob/master/usyslog.py)

Upload the required modules, and the optional modules, as needed, to your application.

## Basic Usage

The `ulog` module provides basic logging facilites for logging events in your application.  By default, events are logged to the console, but this behavior is configurable.

For the most basic usage of this module, use the convenience functions that are exposed on the `ulog` module, e.g.,

    >>> import ulog
    >>> ulog.info("Beware the Jabberwock, my son!")
    2000-01-01T15:11:16.005 [info] esp8266: Beware the Jabberwock, my son!
    >>> ulog.info("The jaws that bite, the claws that catch!")
    2000-01-01T15:11:26.005 [info] esp8266: The jaws that bite, the claws that catch!
    >>> ulog.warning("Beware the Jubjub bird, and shun")
    2000-01-01T15:11:36.005 [warning] esp8266: Beware the Jubjub bird, and shun
    >>> ulog.error("The frumious Bandersnatch!")
    2000-01-01T15:11:46.005 [error] esp8266: The frumious Bandersnatch!

## Default Logger Configuration

The default logger is stored in the `ulog.logger` variable, and may be configured through the `log_config.py` module, if it is found on the python path.

This configuration file supports the following settings:

    ##
    ## Name: name
    ## Type: string
    ## Required: no
    ## Default: "esp8266"
    ## Description: The name of the logger instance.  This name will be provided 
    ## as a component to all log messages sent through this logger instance.
    ## Example:
    ## name="esp8266"


    ## 
    ## Name: levels
    ## Type: [level], where level is one of: 'debug', 'info', 'warning', 'error'
    ## Required: no
    ## Default: ['info', 'warning', 'error']
    ## Description: The list of log levels to log to
    ## Example:
    ## levels=['info', 'warning', 'error']

    ##
    ## Name: sinks
    ## Type: Dictionary 
    ## Required: no
    ## Default: {'console': None}
    ## Description: A specification of the sinks to instantiate in this logger instance.
    ## This dictionary is of the form {<name>: <config>}, where <name> is a sink name
    ## corresponding to a module called <name>_sink, and <config>
    ## is a dictionary (or None) whose structure is specific to the sink type.
    ## Example:
    ## sinks = {
    ##     'console': None,
    ##     'syslog': {
    ##         'host': '192.168.1.202',
    ##         'port': 514
    ##     }
    ## }

## `console` sink

The console log sink (`console_sink.py`) logs entries to the console.  This sink requires no configuration.

## `syslog` sink

The syslog sink (`syslog_sink.py`) logs entries to an RFC 5424 sylog server over UDP running on your network.  This sink requires the following configuration:

* `host` (string)  The host on which the syslog server is running
* `port` (integer) The port on which the syslog server is listening

> Note.  You must also install the [`usyslog`](https://github.com/kfricke/micropython-usyslog/blob/master/usyslog.py) module in order to use the syslog sink.


> TODO document how to create your own logging instances

> TODO document how to write log sinks
