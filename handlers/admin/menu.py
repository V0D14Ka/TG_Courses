from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from create_bot import db, bot, inline_admin
from handlers.general.menu import list_categories
from static import messages


async def list_sub_admin(callback: types.CallbackQuery, category, **kwargs):
    markup = await inline_admin.category_keyboard(category)
    await callback.message.edit_reply_markup(markup)


async def item_info_admin(callback: types.CallbackQuery, category, item_id, **kwargs):
    markup = await inline_admin.item_info(category, item_id)
    await callback.message.edit_reply_markup(markup)


async def admin_navigate(call: types.CallbackQuery, callback_data: dict):
    print("Я был в navigate")
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')

    levels = {
        "0": list_categories,
        "1": list_sub_admin,
        "2": item_info_admin
    }

    current_level_func = levels[current_level]
    await current_level_func(
        call,
        category=category,
        item_id=item_id
    )


def register_handlers_menu_admin(_dp: Dispatcher):
    _dp.register_callback_query_handler(admin_navigate, inline_admin.menu_cd.filter())

