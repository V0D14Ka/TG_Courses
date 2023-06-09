from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from create_bot import db, bot, inline_student
from handlers.general.menu import list_categories
from static import messages


async def list_sub_student(callback: types.CallbackQuery, category, courses, **kwargs):
    markup = await inline_student.category_keyboard(category, courses)
    await callback.message.edit_reply_markup(markup)


async def item_info_student(callback: types.CallbackQuery, category, item_id, **kwargs):
    markup = await inline_student.item_info(category, item_id)
    await callback.message.edit_reply_markup(markup)


async def student_navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')

    match current_level:
        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)
        case "1":
            match category:
                case "1":
                    courses = db.get_courses(category)
                    await call.message.edit_text("Выберите курс")
                    await list_sub_student(call, category=category, item_id=item_id, courses=courses)
                case "2":
                    pass
                case "3":
                    pass
        case "2":
            item = db.get_course(item_id)
            await call.message.edit_text(messages.item_info % (item[1], item[2], item[3], item[4], item[5]))
            await item_info_student(call, item_id=item_id, category=category)


def register_handlers_menu_student(_dp: Dispatcher):
    _dp.register_callback_query_handler(student_navigate, inline_student.menu_cd.filter())

