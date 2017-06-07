import http_api_handler
import uhttpd
import uasyncio as asyncio

class Handler:
    def __init__(self):
        pass
    
    def get(self, api_request):
        print(api_request)
        return {'foo': 'bar'}


def simple_loop():
    while True:
        print("Yeehaw!")
        await asyncio.sleep(1)

api_handler = http_api_handler.Handler([(['test'], Handler())])

loop = asyncio.get_event_loop()
loop.create_task(simple_loop())
server = uhttpd.Server([('/api', api_handler)])
server.run()
