"""Handlers for the app's external root, ``/muster/``."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Request
from safir.dependencies.gafaelfawr import auth_dependency
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler

from ..config import config
from ..exceptions import UnexpectedCookieError, UnexpectedHeaderError
from ..models import AuthInfo, Index, MusterResult

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
