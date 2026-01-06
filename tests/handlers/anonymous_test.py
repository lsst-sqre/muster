"""Tests for the anonymous ingress routes."""

import pytest
from httpx import AsyncClient


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
