import datetime
from typing import Awaitable, Callable

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from dishka import FromDishka
from dishka.integrations.base import wrap_injection

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button

from app.bot.states.support import BanningStatesGroup
from app.services import UserService
from app.bot.keyboards import inline
from app.main.config import settings


async def on_input_id(
    message: Message,
    widget: ManagedTextInput[int],
    dialog_manager: DialogManager,
    value: int,
) -> None:
    dialog_manager.dialog_data['banned_user_id'] = value
    print('work')
    await dialog_manager.switch_to(BanningStatesGroup.DATE_SELECTION)


async def on_date_selected(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    selected_date: datetime.date
) -> None:
    if selected_date < datetime.date.today():
        await callback.answer('Нельзя выбрать дату в прошлом ❗', show_alert=True)
    else:
        dialog_manager.dialog_data['is_forever'] = 0
        dialog_manager.dialog_data['date'] = selected_date
        await dialog_manager.switch_to(BanningStatesGroup.TIME_SELECTION, show_mode=ShowMode.EDIT)


async def on_time_input(
    message: Message,
    widget: ManagedTextInput[str],
    dialog_manager: DialogManager,
    value: str,  
) -> None:
    date = dialog_manager.dialog_data['date']
    
    try:
        time_input = datetime.datetime.strptime(value, "%H:%M").time()

        if time_input < datetime.datetime.now().time() and date == datetime.date.today():
            await message.answer('Нельзя выбрать время в прошлом ❗')
        else:
            datetime.time(hour=int(value[:2]), minute=int(value[3:]))
            dialog_manager.dialog_data['time'] = value
            await dialog_manager.switch_to(BanningStatesGroup.CONFIRMATION)
    except Exception as _ex:
        print(_ex)
        await message.answer('Вы ввели время в неправильном формате! Напишите время в формате <b>час:минута</b>')



async def on_cancel_banning(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    await callback_query.answer('Вы успешно отменили блокировку!')
    await callback_query.message.delete()
    await dialog_manager.done()


async def on_forever_ban(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.dialog_data['is_forever'] = 1
    await dialog_manager.switch_to(BanningStatesGroup.CONFIRMATION)


def inject_on_click(func: Callable) -> Awaitable:
    return wrap_injection(
        func=func,
        container_getter=lambda p, _: p[2].middleware_data["dishka_container"],
        is_async=True,
        remove_depends=True,
     )


@inject_on_click
async def on_user_ban(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    is_forever = dialog_manager.dialog_data['is_forever']
    ban_user_id = dialog_manager.dialog_data['banned_user_id']
    info_message_id = dialog_manager.dialog_data['info_message_id']
    
    if is_forever == 0:
        time_str = dialog_manager.dialog_data['time']
        date = dialog_manager.dialog_data['date']
    
        hour, minute = map(int, time_str.split(':'))
        unban_time = datetime.datetime(date.year, date.month, date.day, hour, minute)

        try:
            await user_service.ban(
                user_id=ban_user_id,
                unban_time=unban_time,
                bot=callback_query.bot,
                info_message_id=info_message_id,
                language_code=callback_query.from_user.language_code
            )
            await callback_query.answer('Вы успешно заблокировали пользователя!', show_alert=True)
            await callback_query.message.delete()
            await callback_query.bot.edit_message_text(
                chat_id=settings.SUPERGROUP_ID,
                message_id=info_message_id,
                text=f'''
<b>INFO</b>
<b>🪪 ID</b>: <code>{ban_user_id}</code>
<b>👤 Пользователь:</b> <a href="tg://user?id={ban_user_id}">профиль</a>
<b>👅 Язык:</b> {callback_query.from_user.language_code}
<b>Статус:</b> Заблокирован''',
    reply_markup=inline.unban_kb_markup(user_id=ban_user_id, info_message_id=info_message_id)
            )
        except Exception as _ex:
            print(_ex)
        finally:
            await dialog_manager.done()
    else:
        try:
            await user_service.ban(user_id=ban_user_id)
            await callback_query.answer('Вы успешно заблокировали пользователя!', show_alert=True)
            await callback_query.message.delete()
            await callback_query.bot.edit_message_text(
                chat_id=settings.SUPERGROUP_ID,
                message_id=info_message_id,
                text=f'''
<b>INFO</b>
<b>🪪 ID</b>: <code>{ban_user_id}</code>
<b>👤 Пользователь:</b> <a href="tg://user?id={ban_user_id}">профиль</a>
<b>👅 Язык:</b> {callback_query.from_user.language_code}
<b>Статус:</b> Заблокирован''',
    reply_markup=inline.unban_kb_markup(user_id=ban_user_id, info_message_id=info_message_id)
            )
        except Exception as _ex:
            print(_ex)
        finally:
            await dialog_manager.done()


async def selectec_banned_user(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    item_id: int,
) -> None:
    dialog_manager.dialog_data['banned_user_id'] = item_id
    await dialog_manager.next()


@inject_on_click
async def on_user_unban(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    banned_user_id = dialog_manager.dialog_data['banned_user_id']
    banned_user = await user_service.get_user(user_id=banned_user_id)
    try:
        await user_service.unban(
            user_id=banned_user_id,
            bot=callback_query.message.bot,
            info_message_id=banned_user.info_message,
            language_code='ru',
        )
        await callback_query.answer('Вы успешно разблокировали пользователя!', show_alert=True)
    except Exception as _ex:
        print(_ex)
    finally:
        await dialog_manager.back()
