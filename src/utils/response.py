"""
This file contains all the utils related to response.
"""

from typing import Any, Optional

from rest_framework.response import Response


class CustomResponse(Response):
    """
    Custom response class that returns data under the key 'data' and any errors
    under the key 'errors', if provided. Behaves like the default Response class.
    """

    def __init__(
        self, *, data: Optional[Any] = None, errors: Optional[Any] = None, **kwargs
    ):
        if isinstance(data, str):
            data = {"message": data}

        if isinstance(errors, str):
            errors = {"message": errors}

        super().__init__(data={"data": data, "errors": errors}, **kwargs)
