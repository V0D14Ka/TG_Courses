import os
import asyncio
import tortoise
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from keyboard.admin.inline_kb import InlineAdmin
from keyboard.student.inline_kb import InlineStudent
from utils import Validation

inline_admin = InlineAdmin()
inline_student = InlineStudent()
storage = MemoryStorage()
validation = Validation()

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)
