import datetime
from typing import Optional, Sequence

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.schemas import User
from app.data.dal import UserDAL
from app.main.config import settings


def supergroup_ban_kb_markup(user_id: int, info_message_id: int = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(text='Заблокировать пользователя', callback_data=f'ban|{user_id}|{info_message_id}')
                ],
            ]
        )
    return kb


class UserService:
    def __init__(self, user_dal: UserDAL) -> None:
        self.user_dal = user_dal
        self.scheduler = AsyncIOScheduler()
    
    async def save_user(self, **kwargs) -> None:
        exists = await self.user_dal.exists(**kwargs)

        if not exists:
            await self.user_dal.add(**kwargs)

    async def get_user(self, **kwargs) -> User:
        user = await self.user_dal.get_one(**kwargs)
        return user
    
    async def get_users(self, **kwargs) -> Sequence[User]:
        users = await self.user_dal.get_all(**kwargs)
        return users

    async def user_referrals(self, **kwargs) -> int:
        count = await self.user_dal.count_referrals(**kwargs)
        return count

    async def is_registered(self, **kwargs) -> bool:
        exists = await self.user_dal.exists(**kwargs)
        return exists
    
    async def unban(
        self,
        user_id: int,
        bot: Bot,
        info_message_id: int,
        language_code: str
    ) -> None:
        await self.user_dal.update(user_id=user_id, status='not banned')
        await bot.edit_message_text(
            chat_id=settings.SUPERGROUP_ID,
            message_id=info_message_id,
            text=f'''
<b>INFO</b>
<b>🪪 ID</b>: <code>{user_id}</code>
<b>👤 Пользователь:</b> <a href="tg://user?id={user_id}">профиль</a>
<b>👅 Язык:</b> {language_code}
<b>Статус:</b> Не заблокирован''',
reply_markup=supergroup_ban_kb_markup(user_id=user_id, info_message_id=info_message_id))

    async def ban(
        self,
        user_id: int,
        bot: Optional[Bot] = None,
        info_message_id: Optional[int] = None,
        language_code: Optional[str] = None,
        unban_time: Optional[datetime.datetime] = None,
    ) -> None:
        await self.user_dal.update(user_id=user_id, status='banned', unban_at=unban_time)

        if unban_time:
            self.scheduler.add_job(
                func=self.unban,
                trigger='date',
                run_date=unban_time,
                kwargs={
                    'user_id': user_id,
                    'bot': bot,
                    'info_message_id': info_message_id,
                    'language_code': language_code
                }
            )
            self.scheduler.start()
        else:
            pass