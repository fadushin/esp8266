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

