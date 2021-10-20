import json


class RequestArgument:
    def __init__(self, type, location="requestBody", description="", required=True):
        supported_locations = ["requestBody", "query"]
        if not location in supported_locations:
            raise Exception(
                "location {} is not supported, currently supported locations are: {}".format(
                    location, supported_locations
                )
            )
        self.type = type
        self.location = location
        self.description = description
        self.required = required

    def __str__(self):
        return json.dumps(self.__dict__)
