"""Models for muster."""

from pydantic import BaseModel, Field
from safir.metadata import Metadata as SafirMetadata

__all__ = ["Index", "MusterResult"]


class Index(BaseModel):
    """Metadata returned by the external root URL of the application."""

    metadata: SafirMetadata = Field(..., title="Package metadata")

    anonymous_url: str = Field(..., title="Anonymous route test")


class MusterResult(BaseModel):
    """Result for muster tests that don't return other data.

    Generally, ``ok`` will never be set to `False`. Instead, muster will raise
    an exception on failure that will return a 500 error to the caller.
    """

    ok: bool = Field(True, title="Test success")
