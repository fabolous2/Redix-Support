from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Chat, Message
from aiogram.fsm.context import FSMContext

from aiogram_dialog import DialogManager, StartMode

from dishka import FromDishka

from app.bot.states import BanningStatesGroup, StartMessageStatesGroup, BannedUsersSG
from app.main.config import settings
from app.bot.keyboards import inline
from app.services import UserService
from app.bot.utils.json_getter import edit_start_message


router = Router()


#USER BANNING IN THE BOT BY USER_ID
@router.callback_query(F.data == 'ban_user')
async def banning_handler(
    query: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=BanningStatesGroup.USER_ID,
        mode=StartMode.RESET_STACK
    )


#USER BANNING IN GROUP
@router.callback_query(F.data.startswith('ban'))
async def ban_user_handler(
    query: CallbackQuery,
    bot: Bot,
    event_chat: Chat,
    dialog_manager: DialogManager,
) -> None:
    user_id = query.from_user.id
    ban_user_id = query.data.split('|')[1]

    if event_chat.id != user_id:
        await query.answer('Процесс блокировки находиться в вашем чате с ботом!')
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=settings.SUPERGROUP_ID,
            message_id=query.message.message_id,
            caption='some new',
            reply_markup=inline.supergroup_ban_kb_markup(user_id=ban_user_id, info_message_id=query.message.message_id)
        )
    else:
        await dialog_manager.start(
            state=BanningStatesGroup.DATE_SELECTION,
            mode=StartMode.RESET_STACK,
        )
        info_message_id = query.data.split('|')[-1]
        dialog_manager.dialog_data['banned_user_id'] = ban_user_id
        dialog_manager.dialog_data['info_message_id'] = info_message_id


@router.callback_query(F.data == 'list')
async def banned_users_handler(
    query: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    print('work list')
    await dialog_manager.start(state=BannedUsersSG.USER_SELECTION, mode=StartMode.RESET_STACK)


#START MESSAGE EDITING
@router.callback_query(F.data == 'edit_start_message')
async def ban_user_handler(
    query: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:
    await query.message.edit_text('Напишите новое стартовое сообщение.')
    await state.set_state(StartMessageStatesGroup.NEW_MESSAGE)


@router.message(StartMessageStatesGroup.NEW_MESSAGE)
async def ban_user_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
) -> None:
    try:
        edit_start_message(new_message=message.text)
        await message.answer('Вы успешно изменили стартовое сообщение!')
    except Exception as _ex:
        print(_ex)
        await message.answer('Упс... Что-то пошло не так.')
    finally:
        await state.clear()

        


#UNBANNING
@router.callback_query(F.data.startswith('unban'))
async def ban_user_handler(
    query: CallbackQuery,
    bot: Bot,
    user_service: FromDishka[UserService]
) -> None:
    banned_user_id = query.data.split('|')[1]
    info_message_id = query.data.split('|')[-1]
    await query.answer('Вы успешно разблокировали пользователя!', show_alert=True)
    await user_service.unban(
        user_id=banned_user_id,
        bot=bot,
        info_message_id=info_message_id,
        language_code=query.from_user.language_code
    )
