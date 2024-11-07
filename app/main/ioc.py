from typing import AsyncGenerator

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from app.main.config import settings
from app.data.dal import UserDAL
from app.services import UserService

class DatabaseProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(url=settings.DATABASE_URL)

    @provide(scope=Scope.APP, provides=async_sessionmaker[AsyncSession])
    def get_async_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def get_async_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            yield session



class DALProvider(Provider):
    user_dal = provide(UserDAL, scope=Scope.REQUEST, provides=UserDAL)


class ServiceProvider(Provider):
    user_service = provide(UserService, scope=Scope.REQUEST, provides=UserService)
