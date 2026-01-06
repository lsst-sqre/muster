"""Tests for the muster.handlers.external module and routes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from muster.config import config


@pytest.mark.asyncio
async def test_get_index(client: AsyncClient) -> None:
    """Test ``GET /muster/``."""
    response = await client.get("/muster/")
    assert response.status_code == 200
    data = response.json()
    assert data["anonymous_url"] == "https://example.com/muster/anonymous"
    metadata = data["metadata"]
    assert metadata["name"] == config.name
    assert isinstance(metadata["version"], str)
    assert isinstance(metadata["description"], str)
    assert isinstance(metadata["repository_url"], str)
    assert isinstance(metadata["documentation_url"], str)


@pytest.mark.asyncio
async def test_get_anonymous(client: AsyncClient) -> None:
    r = await client.get(
        "/muster/anonymous",
        headers={"X-Some-Header": "foo", "Cookie": "some-cookie=foo"},
    )
    assert r.status_code == 200

    r = await client.get(
        "/muster/anonymous", headers={"Authorization": "bearer some-token"}
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "loc": ["header", "Authorization"],
                "msg": "Header Authorization set but should not be present",
                "type": "unexpected_header",
            }
        ]
    }

    r = await client.get(
        "/muster/anonymous", headers={"Cookie": "gafaelfawr=some-cookie"}
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "loc": ["header", "Cookie"],
                "msg": "Cookie gafaelfawr set but should not be present",
                "type": "unexpected_cookie",
            }
        ]
    }
