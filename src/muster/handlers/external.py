"""Handlers for the app's external root, ``/muster/``."""

from fastapi import APIRouter, Request
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler

from ..config import config
from ..exceptions import UnexpectedCookieError, UnexpectedHeaderError
from ..models import Index, MusterResult

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
        metadata=metadata, anonymous_url=str(request.url_for("get_anonymous"))
    )


@external_router.get("/anonymous", summary="Test anonymous ingress")
async def get_anonymous(request: Request) -> MusterResult:
    if request.headers.get("Authorization"):
        raise UnexpectedHeaderError("Authorization")
    if request.cookies.get("gafaelfawr"):
        raise UnexpectedCookieError("gafaelfawr")
    return MusterResult()
