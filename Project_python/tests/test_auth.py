import pytest
from app.database import UserService, TokenChange

data_for_registration = {
    "name": "test_user",
    "email": "test@example.com",
    "password": "testik"
}


@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_login(client, session):
    try:
        await UserService.register_user(session,
                                        name=data_for_registration["name"],
                                        email=data_for_registration["email"],
                                        password=data_for_registration['password']
                                        )

        data = {
            "email": data_for_registration["email"],
            "password": data_for_registration["password"]
        }
        response = await client.post('/users/login', json=data)
        assert response.status_code == 200  # Проверка статус кода валидной регистрации
        assert response.json()["Login"] == "OK"  # Чек валидной регистрации
    finally:
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.order(3)
async def test_login_wrong(client):
    wrong_response = await client.post('/users/login', json={"email": "wrong@mail.ru", "password": "12345"})
    assert wrong_response.status_code == 401  # проверка статус кода невалидной регистрации
    assert wrong_response.json()["Login"] == "Failed"  # Проверка ответа


@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_login_wrong_password(client, session):
    try:
        wrong_password = await client.post('/users/login',
                                           json={"email": data_for_registration["email"], "password": "12345"})
        assert wrong_password.status_code == 401  # код невалидного пароля
        assert wrong_password.json() == {"error": "Неверный пароль"}  # json невалидного пароля
    finally:
        assert await TokenChange.token_delete(session, data_for_registration["email"])  # Чек записи и очистка refresh
        assert await UserService.delete_user(session, data_for_registration["name"])  # Проверка записи и очистка юзера
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.order(4)
async def test_registration(client, session):
    try:

        response = await client.post("/users/registration", json=data_for_registration)
        assert response.status_code == 200  # assert проверки статус кода ответа

    finally:
        assert await UserService.delete_user(session, data_for_registration["name"])  # Проверка записи и очистка юзера
        assert await TokenChange.token_delete(session, data_for_registration["email"])  # Чек записи и очистка refresh
        await session.commit()


# Дописать неверную регистрацию
@pytest.mark.asyncio
@pytest.mark.order(5)
async def test__wrong_email_registration(client, session):
    response = await client.post("/users/registration", json={"name": "Jack", "email": "jack@m", "password": "11"})
    assert response.status_code == 422  # assert проверки статус кода ответа
    assert response.json()["detail"][0]["loc"] == ["body", "email"]


@pytest.mark.asyncio
@pytest.mark.order(6)
async def test_wrong_password_registration(client, session):
    response = await client.post("/users/registration",
                                 json={"name": "Jack", "email": "jack@mail.ru", "password": "11"})
    assert response.status_code == 422  # assert проверки статус кода ответа
    assert response.json()["detail"][0]["msg"] == "String should have at least 6 characters"


@pytest.mark.asyncio
@pytest.mark.order(7)
async def test_wrong_name_registration(client, session):
    response = await client.post("/users/registration", json={"name": "J", "email": "jack@mail.ru", "password": "11"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 3 characters"
