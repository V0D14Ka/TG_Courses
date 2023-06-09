from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from create_bot import db, bot, inline_admin
from handlers.general.menu import list_categories
from static import messages


async def list_sub_admin(callback: types.CallbackQuery, category, courses, **kwargs):
    markup = await inline_admin.category_keyboard(category, courses)
    await callback.message.edit_reply_markup(markup)


async def item_info_admin(callback: types.CallbackQuery, category, item_id, **kwargs):
    markup = await inline_admin.item_info(category, item_id)
    await callback.message.edit_reply_markup(markup)


async def admin_navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')

    match current_level:
        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)
        case "1":
            courses = db.get_courses(category)
            await call.message.edit_text("Выберите курс")
            await list_sub_admin(call, category=category, item_id=item_id, courses=courses)
        case "2":
            item = db.get_course(item_id)
            await call.message.edit_text(messages.item_info % (item[1], item[2], item[3], item[4], item[5]))
            await item_info_admin(call, item_id=item_id, category=category)

    levels = {
        "0": list_categories,
        "1": list_sub_admin,
        "2": item_info_admin
    }

    # current_level_func = levels[current_level]
    # await current_level_func(
    #     call,
    #     category=category,
    #     item_id=item_id,
    #     courses=courses
    # )


def register_handlers_menu_admin(_dp: Dispatcher):
    _dp.register_callback_query_handler(admin_navigate, inline_admin.menu_cd.filter())
