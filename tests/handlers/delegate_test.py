"""Tests for the simple authenticated ingress routes."""

import pytest
from httpx import AsyncClient
from rubin.gafaelfawr import (
    GafaelfawrGroup,
    GafaelfawrUserInfo,
    MockGafaelfawr,
)


@pytest.mark.asyncio
async def test_get_delegated(
    client: AsyncClient, mock_gafaelfawr: MockGafaelfawr
) -> None:
    token = mock_gafaelfawr.create_token("user")
    user_info = GafaelfawrUserInfo(
        username="user",
        email="someuser@example.com",
        name="Some User",
        uid=1234,
        gid=5678,
        groups=[GafaelfawrGroup(name="group-a", id=9999)],
    )
    mock_gafaelfawr.set_user_info("user", user_info)

    r = await client.get(
        "/muster/delegated/header",
        headers={
            "X-Auth-Request-User": "user",
            "X-Auth-Request-Email": "someuser@example.com",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 200
    assert r.json() == {
        "username": "user",
        "email": "someuser@example.com",
        "name": "Some User",
        "uid": 1234,
        "gid": 5678,
        "groups": [{"name": "group-a", "id": 9999}],
    }

    r = await client.get(
        "/muster/delegated/header",
        headers={
            "X-Auth-Request-User": "otheruser",
            "X-Auth-Request-Email": "someuser@example.com",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "msg": (
                    "Gafaelfawr username mismatch: user from user-info"
                    " endpoint, otheruser from request headers"
                ),
                "type": "gafaelfawr_data",
            }
        ]
    }

    r = await client.get(
        "/muster/delegated/header",
        headers={
            "X-Auth-Request-User": "user",
            "X-Auth-Request-Email": "othermail@example.com",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "msg": (
                    "Gafaelfawr email mismatch: someuser@example.com from"
                    " user-info endpoint, othermail@example.com from request"
                    " headers"
                ),
                "type": "gafaelfawr_data",
            }
        ]
    }


@pytest.mark.asyncio
async def test_authorization(
    client: AsyncClient, mock_gafaelfawr: MockGafaelfawr
) -> None:
    token = mock_gafaelfawr.create_token("user")
    mock_gafaelfawr.set_user_info("user", GafaelfawrUserInfo(username="user"))

    r = await client.get(
        "/muster/delegated/authorization",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Auth-Request-User": "user",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 200
    assert r.json() == {"username": "user"}

    r = await client.get(
        "/muster/delegated/authorization",
        headers={
            "X-Auth-Request-User": "user",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "loc": ["header", "Authorization"],
                "msg": "Header Authorization not present but should be set",
                "type": "missing_header",
            }
        ]
    }

    r = await client.get(
        "/muster/delegated/authorization",
        headers={
            "Authorization": "Bearer some-token",
            "X-Auth-Request-User": "user",
            "X-Auth-Request-Token": token,
        },
    )
    assert r.status_code == 500
    assert r.json() == {
        "detail": [
            {
                "loc": ["header", "Authorization"],
                "msg": (
                    "Header Authorization has an incorrect value: Bearer"
                    " some-token"
                ),
                "type": "incorrect_header",
            }
        ]
    }
