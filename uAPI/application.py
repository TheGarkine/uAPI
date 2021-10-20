# never actually import this, we just use it for type hints
try:
    from typing import Dict, Callable, Union
except:
    pass

import usocket as socket
import json
import time
import uasyncio as asyncio
import gc

from .http_error import HTTPError
from .http_response import HTTPResponse
from .request_argument import RequestArgument
from .utils import _SWAGGER_UI_HTML, TYPE_LOOKUP, clean_query_string


class uAPI:
    """uAPI class
    -----------------------
    The general uAPI class for handling the API interactions."""

    running = False
    """Whether or not the server is running. Setting this from true to false, stops the server but setting this from False to true without invoking run() does not start it."""

    def __init__(
        self,
        port: int = 80,
        title: str = "uAPI",
        description: str = "Built with uAPI",
        version: str = "1.0.0",
    ):
        """Constructor for a new uAPI. Predefines the routes /openapi.json and /docs.

        Args:
            port (int, optional): The port for the API to run on. Defaults to 80.
            title (str, optional): Title of the API used in the openapi.json and therefore in /docs. Defaults to "uAPI".
            description (str, optional): Description of the API used in the openapi.json and therefore in /docs. Defaults to "Built with uAPI".
            version (str, optional): Current version of the API used in /openapi.json and therefore in /docs. Defaults to "1.0.0".
        """
        self.title = title
        self.version = version
        self.description = description
        self.port = port

        self._socket = None

        self.routes = {
            "/docs": {
                "GET": {"function": self._swagger_ui, "internal": True, "args": {}}
            },
            "/openapi.json": {
                "GET": {
                    "function": self.generate_openapi_definition,
                    "internal": True,
                    "args": {},
                }
            },
        }

        self._stopped = False

    def endpoint(self, route: str, method: str, args={}, description="") -> Callable:
        """Meant to be used as a decorator around your function. Adds your function as an API endpoint on the given route and method.

        If you have arguments make sure that those are added to the 'args' parameter, such that they can be given to your function later on.

        Args:
            route ([str]): The route to add your api endpoint to. Should be preceded by a '/'. (e.g.: /cats)
            method ([str]): The method for your endpoint. (e.g. "GET" or "POST")
            args (Dict[str, Union[type, RequestArgument]], optional): The arguments for your endpoint. Need to be key value pairs, where the key is a string containing the name of the variable, and the value can either be a RequestArgument object or an allowed type. Types values are equal to undescribed request arguments in the body. Defaults to {}.
            description (str, optional): [description]. Defaults to "".

        Raises:
            Exception: If the endpoint is already configured.

        Returns:
            Callable: the decorated function, without invocation
        """
        if not route in self.routes:
            self.routes[route] = dict()

        if method in self.routes[route]:
            raise Exception("{} {} is already configured".format(method, route))

        def _decorator(func):
            # convert all simple arguments to request arguments
            for arg in args:
                if not isinstance(args[arg], RequestArgument):
                    args[arg] = RequestArgument(args[arg])

            self.routes[route][method] = {
                "description": description,
                "function": func,
                "operationId": func.__name__,
                "internal": False,
                "args": args,
            }

            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return _wrapper

        return _decorator

    def generate_openapi_definition(self) -> dict:
        """Generates an openapi style dict with the current configuration.

        Returns:
            dict: The openapi definition of the API.
        """
        # check https://swagger.io/specification/
        paths = dict()

        for route in self.routes:
            method_dict = dict()
            for method in self.routes[route]:
                if not self.routes[route][method]["internal"]:
                    method_dict[method.lower()] = {
                        "operationId": self.routes[route][method]["operationId"],
                        "description": self.routes[route][method]["description"],
                        "summary": " ".join(
                            self.routes[route][method]["operationId"].split("_")
                        ),
                        "responses": {"200": {"description": "success"}},
                    }
                    if self.routes[route][method]["args"]:
                        request_body_props = {}
                        paramters = []
                        for arg in self.routes[route][method]["args"]:
                            request_argument = self.routes[route][method]["args"][arg]
                            if request_argument.location == "requestBody":
                                request_body_props[arg] = {
                                    "type": TYPE_LOOKUP[request_argument.type],
                                    "description": request_argument.description,
                                    "required": str(request_argument.required).lower(),
                                }
                            else:
                                paramters.append(
                                    {
                                        "name": arg,
                                        "in": request_argument.location,
                                        "description": request_argument.description,
                                        "required": request_argument.required,
                                    }
                                )
                        if paramters:
                            method_dict[method.lower()]["parameters"] = paramters

                        if request_body_props:
                            method_dict[method.lower()]["requestBody"] = {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": request_body_props,
                                        }
                                    }
                                }
                            }

            if len(method_dict) > 0:
                paths[route] = method_dict

        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
            },
            "paths": paths,
        }

        return openapi

    def _swagger_ui(self) -> HTTPResponse:
        """Returns a browsable representation for the API in HTML.

        Returns:
            HTTPResponse: [description]
        """
        return HTTPResponse(data=_SWAGGER_UI_HTML, content_type="text/html")

    async def _process_connection(self, connection: socket.socket):
        """Processes a request on a new connection.

        Args:
            connection (socket.socket): The connection to process communication on.
        """
        try:
            request = connection.recv(8 * 1024).decode("ASCII")

            lines = request.split("\r\n")
            method, path, _ = lines[0].split(" ")

            question_marks = path.count("?")
            if question_marks == 0:
                route = path
                query = ""
            elif question_marks == 1:
                route, query = path.split("?")
            else:
                raise HTTPError(400, "Invalid URL format!")

            print("{}\t: {} {}".format(time.time(), method, route))

            if not route in self.routes:
                raise HTTPError(404)

            route = self.routes[route]
            if method not in route:
                raise HTTPError(405)

            query_fragments = query.split("&")
            query_params = {}
            for fragment in query_fragments:
                if fragment.count("=") == 1:
                    key, val = [clean_query_string(i) for i in fragment.split("=")]
                    query_params[key] = val

            args = {}
            if route[method]["args"]:
                body = lines[-1]
                validationError = {}
                parsed_body = {}
                if len(body) > 0:
                    try:
                        parsed_body = json.loads(body)
                    except:
                        raise HTTPError(400, "Invalid format in body, allowed: JSON!")
                for arg in route[method]["args"]:
                    request_argument: RequestArgument = route[method]["args"][arg]
                    if request_argument.location == "requestBody":
                        if arg in parsed_body:
                            if isinstance(parsed_body[arg], request_argument.type):
                                args[arg] = parsed_body[arg]
                                del parsed_body[arg]
                            else:
                                validationError[arg] = {
                                    "error": "wrong type, expected {}, got {}".format(
                                        request_argument.type, type(parsed_body[arg])
                                    ),
                                    "location": "requestBody",
                                }
                        else:
                            if request_argument.required:
                                validationError[arg] = {
                                    "error": "required but missing",
                                    "location": "requestBody",
                                }

                    if request_argument.location == "query":
                        if arg in query_params:
                            try:
                                args[arg] = request_argument.type(query_params[arg])
                                del query_params[arg]
                            except Exception as e:
                                validationError[arg] = {
                                    "error": "wrong type, expected {},input: {}".format(
                                        request_argument.type, query_params[arg]
                                    ),
                                    "location": "requestBody",
                                }
                                del query_params[arg]
                        else:
                            if request_argument.required:
                                validationError[arg] = {
                                    "error": "required but missing",
                                    "location": "query",
                                }
                if validationError:
                    raise HTTPError(400, json.dumps(validationError))

            result = route[method]["function"](**args)
            # Wrap the result in an HTTPResponse if it is not already one
            if not isinstance(result, HTTPResponse):
                result = HTTPResponse(data=result)

            connection.send(result.to_HTTP())
            connection.close()
            return

        except HTTPError as e:
            connection.send(e.to_HTTP())
            connection.close()
            return
        except Exception as e:
            error = HTTPError(500, str(e))
            print(e)
            connection.send(error.to_HTTP())
            connection.close()

    async def run(self) -> None:
        """Runs the server while running is set to True. Also sets the running_variable to true.

        Raises:
            Exception: If the server is already running..
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
        self._socket.bind(addr)
        self._socket.listen(5)

        if self.running:
            raise Exception("The uAPI server is already running!")
        self.running = True
        self._stopped = False
        # this allows other tasks to run in the background
        self._socket.setblocking(False)
        while self.running:
            try:
                gc.collect()
                conn, addr = self._socket.accept()
                print("Got a connection from %s" % str(addr))
                asyncio.create_task(self._process_connection(conn))
                await asyncio.sleep_ms(100)
            except:
                # allow task change
                await asyncio.sleep_ms(100)
        self._stopped = False

    async def stop(self) -> None:
        """Can be called as an blocking function that sets running to false and waits for the server to actually stop."""
        self.running = False
        while not self._stopped:
            await asyncio.sleep_ms(100)

        self._socket.close()
        self._socket = None
