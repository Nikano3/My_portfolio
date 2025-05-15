from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from pydantic import EmailStr
from app.config import settings
import uuid
from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import TokenChange


class Access:
    @staticmethod
    async def create(email: EmailStr):
        exp = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_LIFETIME)
        payload = {
            "email": email,
            "exp": exp
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    async def check(token: str = Header(..., alias="token")):

        try:
            decoded_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return {"valid": True, "expired": False, "data": decoded_data}
        except ExpiredSignatureError:
            return {"valid": False, "expired": True}
        except InvalidTokenError:
            return {"valid": False, "expired": False}


class Refresh:
    def __init__(self):
        self.access_token = Access()

    @staticmethod
    async def create(db: AsyncSession, email: EmailStr, expires_delta: timedelta = timedelta(days=30)):

        time = datetime.now(timezone.utc)
        exp = time + expires_delta
        iat = time
        jti = uuid.uuid4()
        data = {
            "email": email,
            "exp": exp,  # Expiration Time (время истечения)
            "iat": time,  # Issued At (время выпуска)
            "jti": str(jti)  # JWT ID
        }
        await TokenChange.token_create(db, user_email=email, jti=jti, iat=iat, exp=exp)
        return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    async def check(db: AsyncSession, refresh: str):
        try:
            data = jwt.decode(refresh, settings.JWT_SECRET, algorithms=["HS256"])

            jti = uuid.UUID(data["jti"])

            result = await TokenChange.token_check(db, jti)
            print(result)
            if not result:
                return {"valid": False, "expired": False}
            if result.exp < datetime.now(timezone.utc):  # Если токен истёк
                await TokenChange.token_delete(db, result)  # Удаляем токен из базы данных
                return {"valid": False, "expired": True, "error": "Token expired"}

        except DecodeError:
            return {"valid": False, "expired": False, "error": "Invalid token format"}
        return {"valid": True, "expired": False, "email": result.user_email}
