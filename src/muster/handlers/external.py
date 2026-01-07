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
    UnexpectedCookieError,
    UnexpectedHeaderError,
)
from ..models import AuthInfo, Index, MusterResult, UserInfo

__all__ = ["external_router"]

external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(request: Request) -> Index:
    metadata = get_metadata(
        package_name="muster", application_name=config.name
    )
    return Index(
        metadata=metadata,
        anonymous_url=str(request.url_for("get_anonymous")),
        auth_required_url=str(request.url_for("get_auth", mode="fail")),
        auth_redirect_url=str(request.url_for("get_auth", mode="redirect")),
        delegated_url=str(request.url_for("get_delegated")),
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
    response_model_exclude_none=True,
    summary="Test authenticated routes",
)
async def get_auth(
    *,
    mode: Literal["fail", "redirect"],
    user: Annotated[str, Depends(auth_dependency)],
    x_auth_request_email: Annotated[str | None, Header()] = None,
) -> AuthInfo:
    return AuthInfo(username=user, email=x_auth_request_email)


@external_router.get(
    "/delegated",
    response_model_exclude_none=True,
    summary="Test delegated token",
)
async def get_delegated(
    *,
    gafaelfawr: Annotated[GafaelfawrClient, Depends(gafaelfawr_dependency)],
    user: Annotated[str, Depends(auth_dependency)],
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
    return UserInfo.from_gafaelfawr(user_info)
