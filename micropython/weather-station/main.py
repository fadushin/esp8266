import machine

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('Woke from a deep sleep')
else:
    print('Power on or hard reset')

def main() :
    import os
    files = os.listdir()
    if 'ws.py' in files :
        import ws
        ws.station.run()

#import time
#time.sleep(10)
main()
