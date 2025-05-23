from fastapi import HTTPException
from sqlalchemy import DateTime, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.users.models import Users, Refresh
from pydantic import EmailStr
import uuid
from app.utils.password import hash_password, verify_password


class UserService:

    @staticmethod
    async def register_user(session: AsyncSession, name: str, email: EmailStr, password: str):
        hashed_password = hash_password(password)
        user = Users(name=name, password=hashed_password, email=email)
        session.add(user)
        await session.commit()

    @staticmethod
    async def login_check(session: AsyncSession, email: EmailStr, password: str):
        stmt = select(Users).where(Users.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return False

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Неверный пароль")

        return True

    @staticmethod
    async def find_user_name(session: AsyncSession, name: str):
        find = select(Users).where(Users.name == name)
        result = await session.execute(find)
        find = result.scalar_one_or_none()
        if not find:
            raise HTTPException(status_code=404, detail="User do not found")
        return find.id

    @staticmethod
    async def find_user(session: AsyncSession, id: int):
        find = select(Users).where(Users.id == id)
        result = await session.execute(find)
        find = result.scalar_one_or_none()
        if not find:
            raise HTTPException(status_code=404, detail="User do not found")
        return find

    @staticmethod
    async def delete_user(session: AsyncSession, name: str):
        # Сначала ищем пользователя
        stmt = select(Users).where(Users.name == name)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Удаляем пользователя
        await session.delete(user)
        await session.commit()
        return True

    @staticmethod
    async def all_users(session: AsyncSession):
        request = select(Users)
        result = await session.execute(request)
        users = result.scalars().all()
        final = {}
        for user in users:
            final[f"user#{user.id}"] = user
        return final


class TokenChange:
    @staticmethod
    async def token_create(session: AsyncSession, user_email: EmailStr, jti: uuid, iat: DateTime,
                           exp: DateTime):
        await session.execute(
            delete(Refresh).where(Refresh.user_email == user_email)
        )
        await session.commit()
        token = Refresh(user_email=user_email, jti=jti, iat=iat, exp=exp)
        session.add(token)
        await session.commit()

    @staticmethod
    async def token_delete(session: AsyncSession, email: EmailStr):
        find = select(Refresh).where(Refresh.user_email == email)
        result = await session.execute(find)
        token = result.scalar_one_or_none()
        await session.delete(token)
        await session.commit()
        return True

    @staticmethod
    async def token_check(session: AsyncSession, jti: uuid.UUID):
        find = select(Refresh).where(Refresh.jti == jti)
        result = await session.execute(find)
        find = result.scalar_one_or_none()
        if not find:
            return False
        return find
