"""uAPI - A lightweight API framework for microcontrollers

This modules is meant to make development on APIs easier and is inspired by https://github.com/tiangolo/fastapi.

The central class `uAPI` allows to create custom HTTP endpoints, according to ones needs.

Copyright (c) 2021 Raphael Krauthann
Licence: MIT"""

# This also defines the order in which the documentation is generated
__all__ = ["uAPI", "RequestArgument", "HTTPResponse", "HTTPError"]

from .application import uAPI
from .http_error import HTTPError
from .http_response import HTTPResponse
from .request_argument import RequestArgument
from .utils import HTTP_STATUS_CODES, TYPE_LOOKUP, clean_query_string
