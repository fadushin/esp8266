##
## Name: sinks
## Type: [sink], where sink is one of: 'console' or 'syslog'
## Required: yes
## Default: none
## Description: The list of log levels to log to
##
sinks=['console', 'syslog']

##
## Name: levels
## Type: [level], where level is one of: 'debug', 'info', 'warning', 'error'
## Required: yes
## Default: none
## Description: The list of log levels to log to
##
levels=['info', 'warning', 'error']

##
## Name: syslog
## Type: dictionary
## Required: only if syslog sink is configured
## Default: none
## Description: The host and port to send logs to.  
## syslog = {
##     'host': "192.168.1.1",
##     'port': 514
## }