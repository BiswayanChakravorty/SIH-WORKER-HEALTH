"""Pytest test configuration and database initialization fixture."""
import pytest
import pytest_asyncio
from backend.app.database import init_db

@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_db():
    await init_db()
    yield
