"""Tests for the top-level route."""

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
    assert data["auth_cached_url"] == "https://example.com/muster/auth/cached"
    assert data["auth_vinyl_url"] == "https://example.com/muster/auth/vinyl"
    assert data["auth_required_url"] == "https://example.com/muster/auth/fail"
    assert data["auth_redirect_url"] == (
        "https://example.com/muster/auth/redirect"
    )
    assert data["auth_quota_url"] == "https://example.com/muster/auth/quota"
    assert (
        data["delegated_url"] == "https://example.com/muster/delegated/header"
    )
    assert (
        data["authorization_url"]
        == "https://example.com/muster/delegated/authorization"
    )
    metadata = data["metadata"]
    assert metadata["name"] == config.name
    assert isinstance(metadata["version"], str)
    assert isinstance(metadata["description"], str)
    assert isinstance(metadata["repository_url"], str)
    assert isinstance(metadata["documentation_url"], str)
