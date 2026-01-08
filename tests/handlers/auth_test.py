"""Tests for the simple authenticated ingress routes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_auth(client: AsyncClient) -> None:
    for url in (
        "/muster/auth/fail",
        "/muster/auth/redirect",
        "/muster/auth/quota",
    ):
        r = await client.get(url)
        assert r.status_code == 422

        r = await client.get(url, headers={"X-Auth-Request-User": "someuser"})
        assert r.status_code == 200
        assert r.json() == {"username": "someuser"}

        r = await client.get(
            url,
            headers={
                "X-Auth-Request-Email": "someone@example.org",
                "X-Auth-Request-User": "someuser",
            },
        )
        assert r.status_code == 200
        assert r.json() == {
            "username": "someuser",
            "email": "someone@example.org",
        }
