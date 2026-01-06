"""Tests for the top-level route."""

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
