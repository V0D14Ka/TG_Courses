from DB.sqlite_db import db_init
from create_bot import dp
from aiogram.utils import executor
from handlers import start, menu, admin_menu, student_menu

start.register_handlers_start(dp)
menu.register_handlers_menu(dp)
admin_menu.register_handlers_menu_admin(dp)
student_menu.register_handlers_menu_student(dp)


async def on_startup(_):
    await db_init()


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
