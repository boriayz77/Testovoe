import asyncio
import logging
import sys

from aiohttp import web
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
from bot.database.engine import drop_db, create_db
from bot.middelewares.db import DataBaseSession
from bot.parametrs import dp, bot, session_maker, WEBHOOK_PATH, app
from bot.handler.user_private import main_bot_router
from bot.webhook import t_bank_webhook


dp.include_routers(
    main_bot_router,
)



async def on_startup():

    run_param = False
    if run_param:
        await drop_db()
    await create_db()
    return



async def start_webhook_server():
    # Настраиваем SimpleRequestHandler для aiogram
    app.router.add_post(WEBHOOK_PATH, t_bank_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    # Ожидаем завершения
    await asyncio.Event().wait()



async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup()
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await asyncio.gather(
        dp.start_polling(bot),
        start_webhook_server()
    )




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

    # Устанавливаем уровень логирования для SQLAlchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    asyncio.run(main())
