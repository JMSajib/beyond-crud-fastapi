from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# from src.books.models import Book
from src.config import Config

async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=True))


async def init_db():
    async with async_engine.begin():
        pass


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session
