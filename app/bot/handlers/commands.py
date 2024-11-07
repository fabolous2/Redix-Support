from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from app.bot.keyboards import inline
from app.bot.utils.json_getter import get_start_message
from app.main.config import settings


router = Router()


@router.message(CommandStart())
async def start_handler(
    message: Message,
) -> None:
    await message.answer(text=get_start_message())


@router.message(Command('apanel'))
async def support_handler(
    message: Message,
    bot: Bot,
) -> None:
    is_admin = await bot.get_chat_member(chat_id=settings.SUPERGROUP_ID, user_id=message.from_user.id)
    
    if is_admin.status in ('creator', 'administrator', 'member'):
        await message.answer('Добро пожаловать в админ панель! Выберите действия ниже:', reply_markup=inline.apanel_kb_markup)
