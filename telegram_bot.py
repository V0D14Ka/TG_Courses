from create_bot import dp
from aiogram.utils import executor
from handlers import start, menu

start.register_handlers_start(dp)
menu.register_handlers_menu(dp)


async def on_startup(_):
    print("Бот успешно запущен")


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
