from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import Config


async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=True))


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    AsyncSessionMaker = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionMaker() as async_session_maker:
        yield async_session_maker
