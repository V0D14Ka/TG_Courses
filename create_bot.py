import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from DB import BotDB
from keyboard.admin.inline_kb import InlineAdmin
from keyboard.student.inline_kb import InlineStudent

db = BotDB('sqlite.db')

inline_admin = InlineAdmin(db)
inline_student = InlineStudent(db)
storage = MemoryStorage()

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)
