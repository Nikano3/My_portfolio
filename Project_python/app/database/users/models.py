import uuid

from sqlalchemy import Column, Integer, String, DateTime
import asyncio
from app.database.users.db import engine, Base
from sqlalchemy.dialects.postgresql import UUID


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)


class Refresh(Base):
    __tablename__ = "refresh"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_email = Column(String, nullable=False)
    jti = Column(UUID(as_uuid=True), default=uuid.uuid4)
    iat = Column(DateTime(timezone=True), nullable=False)
    exp = Column(DateTime(timezone=True), nullable=False)

# Функция для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Запуск создания таблиц
async def main():
    await create_tables()


if __name__ == "__main__":
    asyncio.run(main())  # Запускаем асинхронную функцию