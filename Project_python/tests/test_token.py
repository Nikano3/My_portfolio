import pytest
from app.database import TokenChange
from .data.refresh_token import create_expired_refresh
from app.utils.jwt_operations import Refresh

email = "testik123@mail.ru"


@pytest.mark.asyncio
@pytest.mark.order(8)
async def test_access_refresh(client, session):
    try:

        token = await Refresh.create(session, email)
        response = await client.post("/refresh", headers={"token": token})
        assert response.status_code == 200

    finally:
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.order(9)
async def test_expired_access_refresh(client, session):
    try:
        response = await client.post("/refresh", headers={"token": await create_expired_refresh(session, email)})
        assert response.status_code == 401
        assert response.json() == {"error": "token is expired"}
    finally:
        assert await TokenChange.token_delete(session, email)
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.order(10)
async def test_wrong_access_refresh(client):
    response = await client.post("/refresh", headers={"token": "awdfaeg42e21fhn892h4g02j9d9031jfof"})
    assert response.status_code == 401
    assert response.json() == {"error": "token is not valid"}
