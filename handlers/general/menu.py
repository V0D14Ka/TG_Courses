from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from DB.models import Administrators, Users
from create_bot import bot, inline_admin, inline_student
from static import messages


async def show_menu(message: types.Message):
    if not await Administrators.exists(id=message.from_user.id) and not await Users.exists(id=message.from_user.id):
        await bot.send_message(message.from_user.id, "Для начала работы напишите - /start")
    else:
        await list_categories(message)


async def list_categories(message: Union[types.CallbackQuery, types.Message], **kwargs):

    if Administrators.exists(id=message.from_user.id, is_active=True):
        markup = await inline_admin.menu_keyboard()
    else:
        markup = await inline_student.menu_keyboard()

    if isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)

    if isinstance(message, types.Message):
        await message.answer("Выберите пункт", reply_markup=markup)



def register_handlers_menu(_dp: Dispatcher):
    _dp.register_message_handler(show_menu, commands=['menu'])

