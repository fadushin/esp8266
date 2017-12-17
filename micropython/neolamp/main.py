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
import neolamp
neolamp.run()










# def lavalamp() :
#     np = neolamp.create_neopixel(2, 4)
#     neolamp.clear_pixels(np)
#     ll_config = (
#         (0.5,  5, 64, 0), # red (frequency, amplitude, magnitude, offset)
#         (0.5, 10, 16, 0), # green
#         (0.9, 20, 32, 0)  # blue
#     )
#     ll = neolamp.LavaLamp(np, ll_config, sleep_ms=100, verbose=False).register()
#     run_event_loop()
#
# def schedule_test(mode=neolamp.LINEAR) :
#     ntpupdate()
#     import core.ntpd
#     core.ntpd.Ntpd(15*60*1000).register()
#     np = neolamp.create_neopixel(2, 4)
#     neolamp.clear_pixels(np)
#     def mk_sched(secs, color) :
#         import utime
#         (y, mo, d, h, mi, s, wd, yd) = utime.localtime(secs)
#         return {
#             "time": {
#                 "hour": h,
#                 "minute": mi,
#                 "second": s,
#                 "dow": [1,2,3,4,5]
#             },
#             "color": color
#         }
#     def create_schedule(offset=2) :
#         import utime
#         current_secs = utime.time()
#         return [
#             mk_sched(current_secs, (0, 0, 0)),
#             mk_sched(current_secs + 60*offset, (64, 32, 0)),
#             mk_sched(current_secs + 60*(offset + 1), (0, 0, 0))
#         ]
#     mgr = neolamp.ScheduleManager(np, create_schedule(), mode=mode, verbose=True).register()
#     run_event_loop()
