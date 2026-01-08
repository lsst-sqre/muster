"""Test fixtures for muster tests."""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
import respx
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

pytest.register_assert_rewrite("rubin.gafaelfawr", "rubin.repertoire")

from rubin.gafaelfawr import MockGafaelfawr, register_mock_gafaelfawr
from rubin.repertoire import Discovery, register_mock_discovery

from muster import main


@pytest_asyncio.fixture
async def app() -> AsyncGenerator[FastAPI]:
    """Return a configured test application.

    Wraps the application in a lifespan manager so that startup and shutdown
    events are sent during test execution.
    """
    async with LifespanManager(main.app):
        yield main.app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Return an ``httpx.AsyncClient`` configured to talk to the test app."""
    async with AsyncClient(
        base_url="https://example.com/", transport=ASGITransport(app=app)
    ) as client:
        yield client


@pytest.fixture
def mock_discovery(
    respx_mock: respx.Router,
    monkeypatch: pytest.MonkeyPatch,
) -> Discovery:
    monkeypatch.setenv("REPERTOIRE_BASE_URL", "https://example.com/repertoire")
    path = Path(__file__).parent / "data" / "discovery.json"
    return register_mock_discovery(respx_mock, path)


@pytest_asyncio.fixture
async def mock_gafaelfawr(
    mock_discovery: Discovery, respx_mock: respx.Router
) -> MockGafaelfawr:
    return await register_mock_gafaelfawr(respx_mock)
