import logging
import asyncio

from dishka.integrations.aiogram import setup_dishka
from dishka import make_async_container

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram_dialog import setup_dialogs

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from app.main.config import settings
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider
from app.bot import routers
from app.bot.bot_dialogs.banning import ban_dialog, banned_users_dialog

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    bot = Bot(token=settings.BOT_TOKEN,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Moscow"))

    dispatcher = Dispatcher(scheduler=scheduler)
    scheduler.ctx.add_instance(instance=bot, declared_class=Bot)

    dispatcher.include_router(ban_dialog)
    dispatcher.include_routers(*routers)
    dispatcher.include_router(banned_users_dialog)
    
    container = make_async_container(DatabaseProvider(), DALProvider(), ServiceProvider())
    setup_dishka(container=container, router=dispatcher, auto_inject=True)
    setup_dialogs(dispatcher)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot, skip_updates=True)
    finally:
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")