from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select, exists, delete, Result, func

from app.schemas import User
from app.data.models import UserModel


class UserDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, **kwargs) -> None:
        query = insert(UserModel).values(**kwargs)
        await self.session.execute(query)
        await self.session.commit()

    async def update(self, user_id: int, **kwargs) -> None:
        query = update(UserModel).where(UserModel.user_id == user_id).values(**kwargs)
        await self.session.execute(query)
        await self.session.commit()

    async def exists(self, **kwargs) -> bool:
        query = select(
            exists().where(
                *(
                    getattr(UserModel, key) == value
                    for key, value in kwargs.items()
                    if hasattr(UserModel, key)
                )
            )
        )
        result = await self.session.execute(query)

        return result.scalar_one()

    async def is_column_filled(self, user_id: int, *column_names: str) -> bool:
        # Проверка существования пользователя
        user_exists = await self.exists(user_id=user_id)

        if not user_exists:
            return False  # Пользователь не существует, колонка не заполнена

        query = select(
            *(
                getattr(UserModel, column_name)
                for column_name in column_names
                if hasattr(UserModel, column_name)
            )
        ).where(UserModel.user_id == user_id)

        result = await self.session.execute(query)
        column_value = result.scalar_one_or_none()

        return column_value is not None

    async def _get(self, **kwargs) -> Result[tuple[UserModel]] | None:
        exists = await self.exists(**kwargs)

        if not exists:
            return None

        query = select(UserModel).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result

    async def get_one(self, **kwargs) -> User | None:
        res = await self._get(**kwargs)

        if res:
            db_user = res.scalar_one_or_none()
            return User(
                user_id=db_user.user_id,
                created_at=db_user.created_at,
                topic_id=db_user.topic_id,
                status=db_user.status,
                unban_at=db_user.unban_at,
                info_message=db_user.info_message
            )

    async def get_all(self, **kwargs) -> list[User] | None:
        res = await self._get(**kwargs)

        if res:
            db_users = res.scalars().all()
            return [
                User(
                    user_id=db_user.user_id,
                    created_at=db_user.created_at,
                    topic_id=db_user.topic_id,
                    status=db_user.status,
                    unban_at=db_user.unban_at,
                    info_message=db_user.info_message
                )
                for db_user in db_users
            ]

    async def delete(self, **kwargs) -> None:
        query = delete(UserModel).filter_by(**kwargs)

        await self.session.execute(query)
        await self.session.commit()

    async def count_referrals(self, **kwargs) -> int:
        query = (
            select(func.count(UserModel.referral_id))
            .filter_by(**kwargs)
        )
        res = await self.session.execute(query)
        count = res.scalar_one()

        return count
