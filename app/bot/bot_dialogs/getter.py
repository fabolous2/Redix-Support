from aiogram_dialog import DialogManager

from dishka.integrations.base import wrap_injection
from dishka import FromDishka

from app.services import UserService


def inject_getter(func):
    return wrap_injection(
        func=func,
        container_getter=lambda _, p: p["dishka_container"],
        is_async=True,
    )


async def ban_confirmation_getter(
    dialog_manager: DialogManager,
    **kwargs
):
    try:
        date = dialog_manager.dialog_data['date']
        time = dialog_manager.dialog_data['time']
        user = dialog_manager.dialog_data['banned_user_id']
        is_forever = dialog_manager.dialog_data['is_forever']

        return {
            "ban_datetime": f'{date} {time}',
            "user": user,
            "is_forever": is_forever
        }

    except KeyError: 
        user = dialog_manager.dialog_data['banned_user_id']
        print(user)
        is_forever = dialog_manager.dialog_data['is_forever']
        return {
            "user": user,
            "is_forever": is_forever
        }


@inject_getter
async def banned_users_getter(
    dialog_manager: DialogManager,
    user_service:  FromDishka[UserService],
    **kwargs
):
    banned_users = await user_service.get_users(status='banned')
    return {'banned_users': banned_users, 'is_empty': 0 if banned_users else 1}


@inject_getter
async def banned_user_info_getter(
    dialog_manager: DialogManager,
    user_service:  FromDishka[UserService],
    **kwargs,
):
    banned_user_id = dialog_manager.dialog_data['banned_user_id']
    banned_user = await user_service.get_user(user_id=banned_user_id)
    return {'user': banned_user}
