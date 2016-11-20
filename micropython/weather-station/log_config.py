##
## Name: levels
## Type: [level], where level is one of: 'debug', 'info', 'warning', 'error'
## Required: yes
## Default: none
## Description: The list of log levels to log to
##
levels=['info', 'warning', 'error']

##
## Name: host
## Type: string
## Required: no
## Default: none
## Description: The host to send logs to.  If configured, the logging subsystem will send
## log events over TCP/IP to the host and port configured in this file.
##
# host='192.168.1.1'

##
## Name: port
## Type: integer
## Required: no
## Default: none
## Description: The port to send logs to.  See the host configuration setting above.
##
# port=22
