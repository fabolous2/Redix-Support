from aiogram import F

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    Button,
    Row,
    ScrollingGroup,
    Select,
    PrevPage,
    NextPage,
    CurrentPage,
    Back
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import (
    Const,
    Format
)

from app.bot.bot_dialogs.callbacks import (
    on_input_id,
    on_date_selected,
    on_time_input,
    on_cancel_banning,
    on_user_ban,
    on_forever_ban,
    selectec_banned_user,
    on_user_unban
)
from app.bot.bot_dialogs.getter import ban_confirmation_getter, banned_users_getter, banned_user_info_getter
from app.bot.states.support import BanningStatesGroup, BannedUsersSG


async def close_dialog(_, __, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.done()


ban_dialog = Dialog(
    Window(
        Const('🪪 Напишите <b>ID</b> пользователя, которого желаете заблокировать.'),
        TextInput(
            id='user_id_input',
            on_success=on_input_id,
        ),
        state=BanningStatesGroup.USER_ID,
    ),
    Window(
        Const('📅 Выберите дату, до которой вы хотите забанить пользователя.'),
        Calendar(
            id='date_selection',
            on_click=on_date_selected
        ),
        Button(
            text=Const('🔐 Заблокировать навсегда'),
            id='ban_forever',
            on_click=on_forever_ban,
        ),
        state=BanningStatesGroup.DATE_SELECTION
    ),
    Window(
        Const('Напишите точное время, до которого вы хотите забанить пользователя\n. Напишите время в формате (час:минута). Пример:\n <blockquote>12:00</blockquote>'),
        TextInput(
            id='time_input',
            on_success=on_time_input
        ),
        state=BanningStatesGroup.TIME_SELECTION
    ),
    Window(
        Format('❓ Вы уверены, что хотите забанить данного <a href="tg://user?id={user}">пользователя</a> до <code>{ban_datetime}</code>❓', when=F['is_forever'] == 0),
        Format('❓ Вы уверены, что хотите забанить данного <a href="tg://user?id={user}">пользователя</a> до <code>навсегда</code>❓', when=F['is_forever'] == 1),
        Row(
            Button(
                Const('❌ Отменить блокировку'),
                id='cancel_banning',
                on_click=on_cancel_banning
            ),
            Button(
                Const('✅ Заблокировать'),
                id='ban_user',
                on_click=on_user_ban
            ),
        ),
        state=BanningStatesGroup.CONFIRMATION,
        getter=ban_confirmation_getter
    )
)


banned_users_dialog = Dialog(
    Window(
        Const('Список пуст(', when=F['is_empty'] == 1),
        Const('Список забаненных пользователей', when=F['is_empty'] == 0),
        ScrollingGroup(
            Select(
                id="user_select",
                items="banned_users",
                item_id_getter=lambda item: item.user_id,
                text=Format("№{item.user_id}"),
                on_click=selectec_banned_user,
            ),
            id="users_group",
            height=3,
            width=2,
            hide_on_single_page=True,
            hide_pager=True,
            when=F['is_empty'] == 0
        ),
        Row(
            PrevPage(
                scroll="users_group", text=Format("◀️"),
            ),
            CurrentPage(
                scroll="users_group", text=Format("{current_page1}"),
            ),
            NextPage(
                scroll="users_group", text=Format("▶️"),
            ),
            when=F['is_empty'] == 0
        ),
        state=BannedUsersSG.USER_SELECTION,
        getter=banned_users_getter,
    ),
    Window(
        Format(
'''
<b>INFO:</b>
<b>🪪 ID</b>: <code>{user.user_id}</code>
<b>👤 Пользователь:</b> <a href="tg://user?id={user.user_id}">профиль</a>
'''
        ),
        Button(
            text=Const('🔓 Разблокировать'),
            id='unban',
            on_click=on_user_unban
        ),
        Back(Const('◀️ Назад')),
        state=BannedUsersSG.USER_INFO,
        getter=banned_user_info_getter
    ),
    on_process_result=close_dialog
)
