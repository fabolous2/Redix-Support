from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, Chat
from aiogram.fsm.context import FSMContext

from dishka import FromDishka

from pytz import timezone

from app.main.config import settings
from app.services import UserService
from app.bot.keyboards import inline


router = Router()


@router.message()
async def message_handler(
    message: Message,
    bot: Bot,
    event_chat: Chat,
    # state: FSMContext,
    user_service: FromDishka[UserService]
) -> None:
    # await state.clear()

    user_id = message.from_user.id
    is_registered = await user_service.is_registered(user_id=user_id)
    now = datetime.now(timezone('Europe/Moscow'))
    is_admin = await bot.get_chat_member(chat_id=settings.SUPERGROUP_ID, user_id=user_id)
    topic_id = message.message_thread_id
    available_statuses = ('creator', 'administrator', 'member')

    if is_admin.status not in available_statuses or is_admin.status in available_statuses and topic_id is None:
        if not is_registered:
            forum_topic = await bot.create_forum_topic(chat_id=settings.SUPERGROUP_ID, name=message.from_user.full_name)
            user_info_message = await bot.send_message(
                chat_id=settings.SUPERGROUP_ID,
                message_thread_id=forum_topic.message_thread_id,
                text=f'''
<b>INFO</b>
<b>🪪 ID</b>: <code>{user_id}</code>
<b>👤 Пользователь:</b> <a href="tg://user?id={user_id}">профиль</a>
<b>👅 Язык:</b> {message.from_user.language_code}
<b>Статус:</b> Не заблокирован
                ''',
                reply_markup=inline.supergroup_ban_kb_markup(user_id=user_id)
            )
            await bot.pin_chat_message(chat_id=settings.SUPERGROUP_ID, message_id=user_info_message.message_id)
            await user_service.save_user(
                user_id=user_id,
                created_at=now,
                topic_id=forum_topic.message_thread_id,
                info_message=user_info_message.message_id
            )
            await bot.copy_message(
                chat_id=settings.SUPERGROUP_ID,
                from_chat_id=event_chat.id,
                message_id=message.message_id,
                message_thread_id=forum_topic.message_thread_id
            )
        else:
            user = await user_service.get_user(user_id=user_id)
            if user.status == 'banned':
                if user.unban_at:
                    unban_time = datetime.strftime(user.unban_at, format='%Y-%m-%d %H:%M')
                    await message.answer(f'Вы были заблокированы администрацией до <code>{unban_time}</code> за нарушение правил пользования ботом тех-поддержки!')
                else:
                    await message.answer(f'Вы были заблокированы администрацией <code>навсегда</code> за нарушение правил пользования ботом тех-поддержки!')
            else:
                await bot.copy_message(
                    chat_id=settings.SUPERGROUP_ID,
                    from_chat_id=event_chat.id,
                    message_id=message.message_id,
                    message_thread_id=user.topic_id
                )
                # await bot.forward_message()
    else:
        user = await user_service.get_user(topic_id=topic_id)
        await bot.copy_message(
            chat_id=user.user_id,
            from_chat_id=event_chat.id,
            message_id=message.message_id
        )
