from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

apanel_kb_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Заблокировать пользователя', callback_data='ban_user')
        ],
        [
            InlineKeyboardButton(text='Изменить стартовое сообщение', callback_data=f'edit_start_message')
        ],
        [
            InlineKeyboardButton(text='Заблокированные пользователи', callback_data=f'list')
        ],
    ]
)


def supergroup_ban_kb_markup(user_id: int, info_message_id: int = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(text='Заблокировать пользователя', callback_data=f'ban|{user_id}|{info_message_id}')
                ],
            ]
        )
    return kb


def unban_kb_markup(user_id: int, info_message_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(text='Разблокировать', callback_data=f'unban|{user_id}|{info_message_id}')
                ],
            ]
        )
    return kb