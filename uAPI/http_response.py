import json

from .utils import HTTP_STATUS_CODES


class HTTPResponse:
    """A basic HTTP Response, allows to set custom status_codes and content_types for special requests."""

    def __init__(
        self,
        data: object = None,
        status_code: int = 200,
        content_type: str = "application/json",
    ):
        """Constructor for a HTTP Response.

        Args:
            data (object, optional): The data object, if content_type is application/json, this needs to be parsable. If not it needs a string representation. Defaults to None.
            status_code (int, optional): The status code to be sent to the user. Defaults to 200.
            content_type (str, optional): The content type to be sent to the user. Defaults to "application/json".

        Raises:
            Exception: If the status_code is unknown.
        """
        if status_code not in HTTP_STATUS_CODES:
            raise Exception("status_code {} not known!".format(status_code))
        self.data = data
        self.status_code = status_code
        self.content_type = content_type

    def to_HTTP(self) -> str:
        """Generates a HTTP compatible string to be sent to the client.

        Returns:
            str: The HTTP string.
        """
        if self.data:
            if self.content_type is "application/json":
                data = json.dumps(self.data)
            else:
                data = str(self.data)
        else:
            data = ""

        http = "HTTP/1.1 {} {}\r\n".format(
            self.status_code, HTTP_STATUS_CODES[self.status_code]
        )
        http += "Content-Type: {}\r\n".format(self.content_type)

        if data:
            http += "Content-Length: {}\r\n".format(len(data))
        http += "Connection: close\r\n\r\n"
        http += data

        return http
