from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from data.config import REDIS_PASS
from utils.db_api.postgresql import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host="redis", password=REDIS_PASS)
dp = Dispatcher(bot, storage=storage)
db = dp.loop.run_until_complete(Database.create())
