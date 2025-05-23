import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database.users.db import async_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def session():
    async with async_session() as session:
        yield session


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac