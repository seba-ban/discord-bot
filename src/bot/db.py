from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .settings import DbSettings

settings = DbSettings()
engine = create_async_engine(url=settings.dsn(), echo=True)
session_factory = sessionmaker[AsyncSession](
    engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)
