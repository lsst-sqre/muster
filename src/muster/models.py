"""Models for muster."""

from typing import Annotated

from pydantic import BaseModel, Field
from safir.metadata import Metadata as SafirMetadata

__all__ = ["AuthInfo", "Index", "MusterResult"]


class Index(BaseModel):
    """Metadata returned by the external root URL of the application."""

    metadata: Annotated[SafirMetadata, Field(title="Package metadata")]

    anonymous_url: Annotated[str, Field(title="Anonymous route test")]

    auth_required_url: Annotated[str, Field(title="Auth required test")]

    auth_redirect_url: Annotated[str, Field(title="Auth or redirect test")]


class MusterResult(BaseModel):
    """Result for muster tests that don't return other data.

    Generally, ``ok`` will never be set to `False`. Instead, muster will raise
    an exception on failure that will return a 500 error to the caller.
    """

    ok: Annotated[bool, Field(title="Test success")] = True


class AuthInfo(BaseModel):
    """Result for an authenticated route."""

    username: Annotated[str, Field(title="Authenticated user")]

    email: Annotated[str | None, Field(title="Email of user")] = None
