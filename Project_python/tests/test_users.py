import pytest

from app.database import UserService
from .data.access_tokens import create_valid, create_not_valid, create_expired

data_for_registration = {
    "name": "test_user",
    "email": "test@example.com",
    "password": "testik"
}


class TestUsers:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.order(11)
    async def test_get_users_valid(client):
        response = await client.get("/users", headers=await create_valid())
        assert response.status_code == 200

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.order(12)
    async def test_get_users_invalid(client):
        response = await client.get("/users", headers=await create_not_valid())
        assert response.status_code == 401  # проверка невалидной
        assert response.json() == {"error": "Token is not valid"}

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.order(13)
    async def test_get_users_expired(client):
        response = await client.get("/users", headers=await create_expired())
        assert response.status_code == 401
        assert response.json() == {"error": "Token is expired, go to /refresh"}


class TestUser:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.order(14)
    async def test_get_user_valid(client, session):
        try:
            await UserService.register_user(session,
                                            name=data_for_registration["name"],
                                            email=data_for_registration["email"],
                                            password=data_for_registration['password']
                                            )
            id = await UserService.find_user_name(session, data_for_registration["name"])
            response = await client.get(f"/users/{id}", headers=await create_valid())
            assert response.status_code == 200
        finally:
            assert await UserService.delete_user(session,
                                                 data_for_registration["name"])  # Проверка записи и очистка юзера
            await session.commit()

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.order(15)
    async def test_get_user_token_invalid(client):

        response = await client.get("/users/1", headers=await create_not_valid())
        assert response.status_code == 401  # проверка невалидной
        assert response.json() == {"error": "Token is not valid"}

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_token_expired(client):
        response = await client.get("/users/1", headers=await create_expired())
        assert response.status_code == 401
        assert response.json() == {"error": "Token is expired, go to /refresh"}
