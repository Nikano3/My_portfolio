from datetime import datetime, timezone, timedelta
import jwt
from app.config import settings
import asyncio
async def create_valid():
    exp = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_LIFETIME)
    payload = {
        "email": "test_email@mail.ru",
        "exp": exp
    }

    return {"token": jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")}


async def create_expired():
    exp = datetime.now(timezone.utc) - timedelta(seconds=5)
    payload = {
        "email": "test_email@mail.ru",
        "exp": exp
    }
    return {"token": jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")}


async def create_not_valid():
    exp = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_LIFETIME)
    payload = {
        "email": "test_email@mail.ru",
        "exp": exp
    }
    return {"token": jwt.encode(payload, "wrong", algorithm="HS256")}


a = asyncio.run(create_expired())
print(a)