import uasyncio
from uAPI import uAPI, HTTPResponse

api = uAPI(
    port=8080,
    title="Hello uAPI!",
    description="My First API with uAPI.",
    version="1.0.0",
)


@api.endpoint("/test", "GET")
def hello_world():
    print("Console: Hello World!")
    return HTTPResponse(data="Response: Hello World!", content_type="text/plain")


try:
    uasyncio.run(api.run())
except KeyboardInterrupt:
    print("Stoping")
    api.stop()
