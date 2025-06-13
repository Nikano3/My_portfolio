import uuid
import asyncio
import asyncpg
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database.users.db import engine, Base
from app.config import settings
from app.utils.logger import logger
ADMIN_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}/postgres"
)
async def create_database_if_not_exists():
    conn = await asyncpg.connect(ADMIN_DB_URL)
    dbs = await conn.fetch("SELECT datname FROM pg_database;")
    db_names = [db['datname'] for db in dbs]
    if settings.POSTGRES_DB not in db_names:
        await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}";')
        logger.info(f"✅ Database '{settings.POSTGRES_DB}' create.")
    else:
        logger.warning(f"ℹ️ Database '{settings.POSTGRES_DB}' already exists.")
    await conn.close()

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

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables create.")
async def main():
    await create_database_if_not_exists()
    await create_tables()

if __name__ == "__main__":
    asyncio.run(main())
