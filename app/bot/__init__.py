from .handlers import commands, bot_answers
from .callbacks import apanel

routers = [
    commands.router,
    apanel.router,
    bot_answers.router,
]

__all__ = [
    'routers'
]