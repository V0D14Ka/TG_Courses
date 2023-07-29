import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from keyboard.admin.inline_kb import InlineAdmin
from keyboard.student.inline_kb import InlineStudent
from utils import Validation

load_dotenv()

DADATA_TOKEN = os.getenv("DADATA_TOKEN")
DADATA_SECRET = os.getenv("DADATA_SECRET")

inline_admin = InlineAdmin()
inline_student = InlineStudent()
storage = MemoryStorage()
validation = Validation()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)
