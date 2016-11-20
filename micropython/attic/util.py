def deep_sleep(secs) :
    import machine

    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, secs)

    # put the device to sleep
    machine.deepsleep()

def set_led_error(pin_id=15) :
    import machine
    pin = machine.Pin(pin_id, machine.Pin.OUT)
    pin.high()

def clear_led_error(pin_id=2) :
    import machine
    pin = machine.Pin(pin_id, machine.Pin.OUT)
    pin.low()
    
    
import time

def dht_test(pin=2, n=1, sleep_s=5) :
    import dht
    import machine
    d = dht.DHT11(machine.Pin(pin))
    for i in range(n):
        d.measure()
        line = "temp(f): %s humidity: %s" % (32.0 + 1.8*d.temperature(), d.humidity()) 
        print(line)
        #upload("192.168.1.154", 44404, line)
        upload("KMABOXBO9", "7rwzw8bh", 32.0 + 1.8*d.temperature(), d.humidity())
        #print("Going into deep sleep for %s secs ..." % sleep_secs)
        #deep_sleep(sleep_secs)
        print("Sleeping %s secs ..." % sleep_s)
        time.sleep(sleep_s)
    
def upload(stationid, password, tempf, humidity) :
    import socket
    try :
        #addr_info = socket.getaddrinfo(address, port)
        addr_info = socket.getaddrinfo("weatherstation.wunderground.com", 80)
        url = "/weatherstation/updateweatherstation.php?ID=%s&PASSWORD=%s&dateutc=now&tempf=%s&humidity=%s&softwaretype=ESP8266+DHT11&action=updateraw" % (stationid, password, tempf, humidity)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.connect(addr)
        val = s.send(b"GET %s HTTP/1.0\r\nHost: weatherstation.wunderground.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n" % url)
        print("send val: %s" % val)
        print(s.read())
        s.close()
        send_status("uploaded data")
    except Exception as E :
        print("An error occurred: %s" % E)
        #set_led_error(5)
        import webrepl
        webrepl.start()
        raise Exception("Failed to upload data to wunderground.com: %s" % E)

def send_status(msg, address='192.168.1.154', port=44404) :
    try :
        import socket
        addr_info = socket.getaddrinfo(address, port)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(msg)
        s.close()
        print("Sent %s to %s:%s" % (msg, address, port))
    except Exception as E :
       print("An error occurred sending %s to %s:%s: %s" % (msg, address, port, E))

def blink(pin_id) :
    import machine
    pin = machine.Pin(pin_id, machine.Pin.OUT)
    while True :
        pin.high()
        time.sleep(1)
        pin.low()
        time.sleep(1)


def debug() :
    import os
    print('os.listdir: %s' % os.listdir())
    #import importlib
    #importlib.reload(port_diag)
    import port_diag


def main() :
    print('fd.main: ok')
    #dht_test()

print("Loaded fd.py module")
#main()