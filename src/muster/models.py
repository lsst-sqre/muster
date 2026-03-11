"""Models for muster."""

from typing import Annotated, Self

from pydantic import BaseModel, Field
from rubin.gafaelfawr import GafaelfawrUserInfo
from safir.metadata import Metadata as SafirMetadata

__all__ = ["AuthInfo", "Index", "MusterResult"]


class Index(BaseModel):
    """Metadata returned by the external root URL of the application."""

    metadata: Annotated[SafirMetadata, Field(title="Package metadata")]

    anonymous_url: Annotated[str, Field(title="Anonymous route test")]

    auth_cached_url: Annotated[str, Field(title="Cached auth test")]

    auth_vinyl_url: Annotated[str, Field(title="Vinyl cached auth test")]

    auth_required_url: Annotated[str, Field(title="Auth required test")]

    auth_redirect_url: Annotated[str, Field(title="Auth or redirect test")]

    auth_quota_url: Annotated[str, Field(title="Quota test")]

    delegated_url: Annotated[str, Field(title="Delegated token test")]

    authorization_url: Annotated[str, Field(title="Authorization header test")]


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


class Group(BaseModel):
    """Information about a single group."""

    name: Annotated[str, Field(title="Name of the group")]

    id: Annotated[int, Field(title="Numeric GID of the group")]


class UserInfo(AuthInfo):
    """Result for an authenticated route with a delegated token."""

    name: Annotated[str | None, Field(title="Preferred full name")] = None

    uid: Annotated[int | None, Field(title="UID number")] = None

    gid: Annotated[int | None, Field(title="Primary GID")] = None

    groups: Annotated[list[Group], Field(title="Groups")] = []

    @classmethod
    def from_gafaelfawr(cls, user_info: GafaelfawrUserInfo) -> Self:
        """Create a new object from Gafaelfawr user information."""
        return cls(
            username=user_info.username,
            email=user_info.email,
            name=user_info.name,
            uid=user_info.uid,
            gid=user_info.gid,
            groups=[Group(name=g.name, id=g.id) for g in user_info.groups],
        )
