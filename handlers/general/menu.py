from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from controllers.menu_controller import get_menu, get_category_keyboard, get_item_keyboard, inline_admin, inline_student
from create_bot import db, bot
from static import messages


async def show_menu(message: types.Message):
    await list_categories(message)


async def list_categories(message: Union[types.CallbackQuery, types.Message], **kwargs):
    markup = await get_menu(db.is_admin_exist(message.from_user.id))

    if isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)

    if isinstance(message, types.Message):
        await message.answer("Выберите пункт", reply_markup=markup)


async def list_sub(callback: types.CallbackQuery, category, is_admin, **kwargs):
    markup = await get_category_keyboard(is_admin, category)
    await callback.message.edit_reply_markup(markup)


async def item_info(callback: types.CallbackQuery, category, is_admin, item_id, **kwargs):
    markup = await get_item_keyboard(is_admin, category, item_id)
    await callback.message.edit_reply_markup(markup)


async def navigate(call: types.CallbackQuery, callback_data: dict):
    print("Я был в navigate")
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')
    is_admin = callback_data.get('is_admin')

    levels = {
        "0": list_categories,
        "1": list_sub,
        "2": item_info
    }

    current_level_func = levels[current_level]
    await current_level_func(
        call,
        category=category,
        is_admin=is_admin,
        item_id=item_id
    )


def register_handlers_menu(_dp: Dispatcher):
    _dp.register_message_handler(show_menu, commands=['menu'])
    _dp.register_callback_query_handler(navigate, inline_admin.menu_cd.filter())
    _dp.register_callback_query_handler(navigate, inline_student.menu_cd.filter())
