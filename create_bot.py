import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from DB import BotDB

db = BotDB('sqlite.db')

storage = MemoryStorage()

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)
