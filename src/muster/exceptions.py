"""Exceptions for Muster."""

from typing import ClassVar

from fastapi import Request
from fastapi.responses import JSONResponse
from safir.models import ErrorLocation

__all__ = [
    "MusterError",
    "UnexpectedCookieError",
    "UnexpectedHeaderError",
    "muster_error_handler",
]


class MusterError(Exception):
    """A test performed by Muster failed.

    Exceptions inheriting from this class should set the class variable
    ``error`` to a unique error code (normally composed of lowercase letters
    and underscores) for that error.

    Attributes
    ----------
    location
        The part of the request giving rise to the error. This can be set by
        catching the exception in the part of the code that knows where the
        data came from, setting this attribute, and re-raising the exception.
    field_path
        Field, as a hierarchical list of structure elements, within that part
        of the request giving rise to the error. As with ``location``, can be
        set by catching and re-raising.

    Parameters
    ----------
    message
        Error message, used as the ``msg`` key in the serialized error.
    location
        The part of the request giving rise to the error. This may be omitted
        if the error message does not have meaningful location information, or
        to set this information via the corresponding attribute in a later
        exception handler.
    field_path
        Field, as a hierarchical list of structure elements, within the
        ``location`` giving rise to the error. This may be omitted if the
        error message does not have meaningful location information, or to set
        this information via the corresponding attribute in a later exception
        handler.
    """

    error: ClassVar[str] = "muster_failed"
    """Used as the ``type`` field of the error message.

    Should be overridden by any subclass.
    """

    def __init__(
        self,
        message: str,
        location: ErrorLocation | None = None,
        field_path: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.location = location
        self.field_path = field_path

    def to_dict(self) -> dict[str, list[str] | str]:
        """Convert the exception to a dictionary suitable for the response.

        Returns
        -------
        dict
            Serialized error message in a format suitable as a member of the
            list passed to the ``detail`` parameter to a
            `fastapi.HTTPException`. It is designed to produce the same JSON
            structure as native FastAPI errors.

        Notes
        -----
        The format of the returned dictionary is the same as the serialization
        of `~safir.models.ErrorDetail`, and is meant to be one element in the
        list that is the value of the ``detail`` key.
        """
        result: dict[str, list[str] | str] = {
            "msg": str(self),
            "type": self.error,
        }
        if self.location:
            if self.field_path:
                result["loc"] = [self.location.value, *self.field_path]
            else:
                result["loc"] = [self.location.value]
        return result


class GafaelfawrDataError(MusterError):
    """Some Gafaelfawr information did not match."""

    error = "gafaelfawr_data"


class UnexpectedCookieError(MusterError):
    """Muster saw a cookie that should not have been sent.

    Parameters
    ----------
    cookie_name
        Name of the cookie.
    """

    error = "unexpected_cookie"

    def __init__(self, cookie_name: str) -> None:
        message = f"Cookie {cookie_name} set but should not be present"
        super().__init__(message, ErrorLocation.header, ["Cookie"])


class UnexpectedHeaderError(MusterError):
    """Muster saw a header that should not have been sent.

    Parameters
    ----------
    header_name
        Name of the header
    """

    error = "unexpected_header"

    def __init__(self, header_name: str) -> None:
        message = f"Header {header_name} set but should not be present"
        super().__init__(message, ErrorLocation.header, [header_name])


async def muster_error_handler(
    request: Request, exc: MusterError
) -> JSONResponse:
    """Exception handler for exceptions derived from `MusterError`.

    Parameters
    ----------
    request
        Request that gave rise to the exception.
    exc
        Exception.

    Returns
    -------
    fastapi.JSONResponse
        Serialization of the exception following `~safir.models.ErrorModel`,
        which is compatible with the serialization format used internally by
        FastAPI.
    """
    return JSONResponse(status_code=500, content={"detail": [exc.to_dict()]})
