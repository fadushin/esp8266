import esp
esp.osdebug(None)

##
## These make command-line hacking easier
## remove as part of production
##
from core.cmd import *

##
## load and run neolamp!
##
import http.client
