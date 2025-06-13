from fastapi import HTTPException
from sqlalchemy import DateTime, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.users.models import Users, Refresh
from pydantic import EmailStr
import uuid
from app.utils.password import hash_password, verify_password
from app.utils.logger import logger

class UserService:

    @staticmethod
    async def register_user(session: AsyncSession, name: str, email: EmailStr, password: str):
        try:
            hashed_password = hash_password(password)
            user = Users(name=name, password=hashed_password, email=email)
            session.add(user)
            await session.commit()
            logger.info("User created in database")
        except Exception as e:
            logger.error(f"Error to register user in database: {e}")

    @staticmethod
    async def login_check(session: AsyncSession, email: EmailStr, password: str):

        stmt = select(Users).where(Users.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            logger.error("Login_check: User is not found")
            return False
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        logger.info("login check in database is successfully")

        return True

    @staticmethod
    async def find_user_name(session: AsyncSession, name: str):
        find = select(Users).where(Users.name == name)
        result = await session.execute(find)
        find = result.scalar_one_or_none()
        if not find:
            logger.error("User name is not find in database")
            raise HTTPException(status_code=404, detail="User do not found")
        logger.info("User name find in database")
        return find.id

    @staticmethod
    async def find_user(session: AsyncSession, id: int):
        find = select(Users).where(Users.id == id)
        result = await session.execute(find)
        find = result.scalar_one_or_none()
        if not find:
            logger.error("User is not find in database")
            raise HTTPException(status_code=404, detail="User do not found")
        logger.info("User find in database")
        return find

    @staticmethod
    async def delete_user(session: AsyncSession, name: str):
        # Сначала ищем пользователя
        stmt = select(Users).where(Users.name == name)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.error("User is not find")
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Удаляем пользователя
        await session.delete(user)
        await session.commit()
        logger.info("User delete successfully database")
        return True

    @staticmethod
    async def all_users(session: AsyncSession):
        request = select(Users)
        result = await session.execute(request)
        users = result.scalars().all()
        final = {}
        for user in users:
            final[f"user#{user.id}"] = user
        logger.info("All  users with database is find ")
        return final


class TokenChange:
    @staticmethod
    async def token_create(session: AsyncSession, user_email: EmailStr, jti: uuid, iat: DateTime,
                           exp: DateTime):
        try:
            await session.execute(
                delete(Refresh).where(Refresh.user_email == user_email)
            )
            await session.commit()
            token = Refresh(user_email=user_email, jti=jti, iat=iat, exp=exp)
            session.add(token)
            await session.commit()
            logger.info("Token add to database")
        except Exception as e:
            logger.error(f"Error to add token in database: {e}")
    @staticmethod
    async def token_delete(session: AsyncSession, email: EmailStr):
        try:
            find = select(Refresh).where(Refresh.user_email == email)
            result = await session.execute(find)
            token = result.scalar_one_or_none()
            await session.delete(token)
            await session.commit()
            logger.info("Token in database delete ")
            return True
        except Exception as e:
            logger.error(f"Error to add token in database: {e}")
            return False
    @staticmethod
    async def token_check(session: AsyncSession, jti: uuid.UUID):
        find = select(Refresh).where(Refresh.jti == jti)
        result = await session.execute(find)
        find = result.scalar_one_or_none()

        if not find:
            logger.error("Token is not find in database")
            return False
        logger.info("Token successfully checked")
        return find
