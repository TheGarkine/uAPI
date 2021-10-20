from .utils import HTTP_STATUS_CODES


class HTTPError(Exception):
    """An HTTP error with an status code and description. Use this Exception subtype in your API endpoints to communicate errors like 400"""

    def __init__(self, status_code: int, description: str = None):
        """Constructor for an HTTP error.

        Args:
            status_code (int): The status code to be sent.
            description (str, optional): An optional description that will be sent in the body. Defaults to None.

        Raises:
            Exception: If the status_code is not known.
        """
        if status_code not in HTTP_STATUS_CODES:
            raise Exception("status_code {} not known!".format(status_code))

        self.status_code = status_code
        self.description = description

    def to_HTTP(self) -> str:
        """Converts the error to an HTTP compatible string that can be sent directly to the client.

        Returns:
            str: The error in HTTP format.
        """
        http = "HTTP/1.1 {} {}\r\n".format(
            self.status_code, HTTP_STATUS_CODES[self.status_code]
        )

        if self.description:
            http += "Content-Length: {}\r\n".format(len(self.description))
            http += "Content-Type: text/plain\r\n"
        http += "Connection: keep-alive\r\n\r\n"

        if self.description:
            http += self.description

        return http
