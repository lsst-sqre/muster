"""Handlers for the app's external root, ``/muster/``."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Request
from rubin.gafaelfawr import GafaelfawrClient, gafaelfawr_dependency
from safir.dependencies.gafaelfawr import auth_dependency
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler

from ..config import config
from ..exceptions import (
    GafaelfawrDataError,
    IncorrectHeaderError,
    MissingHeaderError,
    UnexpectedCookieError,
    UnexpectedHeaderError,
)
from ..models import AuthInfo, Index, MusterResult, UserInfo

__all__ = ["external_router"]

external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    response_model_exclude_defaults=True,
    summary="Application metadata",
)
async def get_index(request: Request) -> Index:
    metadata = get_metadata(
        package_name="muster", application_name=config.name
    )
    return Index(
        metadata=metadata,
        anonymous_url=str(request.url_for("get_anonymous")),
        auth_cached_url=str(request.url_for("get_auth", mode="cached")),
        auth_vinyl_url=str(request.url_for("get_auth", mode="vinyl")),
        auth_required_url=str(request.url_for("get_auth", mode="fail")),
        auth_redirect_url=str(request.url_for("get_auth", mode="redirect")),
        auth_quota_url=str(request.url_for("get_auth", mode="quota")),
        delegated_url=str(request.url_for("get_delegated", mode="header")),
        authorization_url=str(
            request.url_for("get_delegated", mode="authorization")
        ),
    )


@external_router.get("/anonymous", summary="Test anonymous ingress")
async def get_anonymous(*, request: Request) -> MusterResult:
    if request.headers.get("Authorization"):
        raise UnexpectedHeaderError("Authorization")
    if request.cookies.get("gafaelfawr"):
        raise UnexpectedCookieError("gafaelfawr")
    return MusterResult()


@external_router.get(
    "/auth/{mode}",
    response_model_exclude_defaults=True,
    summary="Test authenticated routes",
)
async def get_auth(
    *,
    mode: Literal["fail", "redirect", "quota", "cached", "vinyl"],
    user: Annotated[str, Depends(auth_dependency)],
    authorization: Annotated[str | None, Header()] = None,
    x_auth_request_email: Annotated[str | None, Header()] = None,
) -> AuthInfo:
    if authorization:
        raise UnexpectedHeaderError("Authorization")
    return AuthInfo(username=user, email=x_auth_request_email)


@external_router.get(
    "/delegated/{mode}",
    response_model_exclude_defaults=True,
    summary="Test delegated token",
)
async def get_delegated(
    *,
    mode: Literal["header", "authorization"],
    gafaelfawr: Annotated[GafaelfawrClient, Depends(gafaelfawr_dependency)],
    user: Annotated[str, Depends(auth_dependency)],
    authorization: Annotated[str | None, Header()] = None,
    x_auth_request_token: Annotated[str, Header()],
    x_auth_request_email: Annotated[str | None, Header()] = None,
) -> UserInfo:
    user_info = await gafaelfawr.get_user_info(x_auth_request_token)
    if user_info.username != user:
        msg = (
            f"Gafaelfawr username mismatch: {user_info.username} from"
            f" user-info endpoint, {user} from request headers"
        )
        raise GafaelfawrDataError(msg)
    if user_info.email != x_auth_request_email:
        msg = (
            f"Gafaelfawr email mismatch: {user_info.email} from user-info"
            f" endpoint, {x_auth_request_email} from request headers"
        )
        raise GafaelfawrDataError(msg)

    # Authorization should contain the token if and only if the mode is
    # authorization.
    if mode == "authorization":
        if not authorization:
            raise MissingHeaderError("Authorization")
        if authorization != f"Bearer {x_auth_request_token}":
            raise IncorrectHeaderError("Authorization", authorization)
    elif authorization:
        raise UnexpectedHeaderError("Authorization")

    # Return the user iformation from Gafaelfawr.
    return UserInfo.from_gafaelfawr(user_info)
