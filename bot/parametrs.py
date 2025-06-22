import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

CHANNELS = {
    "-1002876584676": "https://t.me/+y-OsL3Jk9_8yNTEy",
    # список каналов
}


TOKEN = os.getenv('TOKEN')
DB_URL = os.getenv('DB_URL')
terminal_key = os.getenv('TERMINAL_KEY')
terminal_password = os.getenv('TERMINAL_PASSWORD')
WEBHOOK_PATH="/t-bank"
dp = Dispatcher()
app = web.Application()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [570491718]
engine = create_async_engine(
    DB_URL,
    echo=True,
    pool_size=10,          # Максимальное количество соединений в пуле
    max_overflow=5,        # Дополнительные соединения, если пул исчерпан
    pool_recycle=300,      # Перезапуск соединений каждые 5 минут
    pool_pre_ping=True     # Проверять соединение перед выдачей из пула
)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


