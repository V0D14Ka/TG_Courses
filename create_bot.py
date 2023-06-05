import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from DB import BotDB
from keyboard.inline_keyboards import Inline

db = BotDB('sqlite.db')

inline_kb = Inline(db)

storage = MemoryStorage()

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)
