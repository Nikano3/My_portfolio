from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from pydantic import EmailStr
from app.config import settings
import uuid
from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import TokenChange
from .logger import logger

class Access:
    @staticmethod
    async def create(email: EmailStr):
        exp = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_LIFETIME)
        payload = {
            "email": email,
            "exp": exp
        }
        logger.info("Access token create successfully")
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    async def check(token: str = Header(..., alias="token")):

        try:
            decoded_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            logger.info("Access Token is approved")
            return {"valid": True, "expired": False, "data": decoded_data}
        except ExpiredSignatureError:
            logger.warning("Access Token is expired")
            return {"valid": True, "expired": True}
        except InvalidTokenError:
            logger.error("Access token is invalid")
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
        logger.info("Refresh token created successfully")
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
                await TokenChange.token_delete(db, result.user_email)
                logger.info("Refresh token is expired")
                return {"valid": False, "expired": True, "error": "Token expired"}
        except ExpiredSignatureError:
            logger.warning("Refresh token is expired")
            return {"valid": False, "expired": True, "error": "Token expired"}
        except DecodeError:
            logger.error("Refresh token is invalid")
            return {"valid": False, "expired": False, "error": "Invalid token format"}
        logger.info("Refresh token is approved")
        return {"valid": True, "expired": False, "email": result.user_email}
