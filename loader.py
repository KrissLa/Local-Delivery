import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from data.config import REDIS_PASS, REDIS_HOST
from utils.db_api.postgresql import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=REDIS_HOST, password=REDIS_PASS)
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()
db = loop.run_until_complete(Database.create())
