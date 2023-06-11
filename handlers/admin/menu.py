from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from create_bot import db, bot, inline_admin
from handlers.general.menu import list_categories
from static import messages
from utils import Validation


# Класс состояния для редактирования
class FSMUpdateItem(StatesGroup):
    new_value = State()


validation = Validation()


# Уровень 1 - курсы по выбранной категории
async def list_sub_admin_menu(callback: types.CallbackQuery, category, courses, **kwargs):
    markup = await inline_admin.category_keyboard(category, courses)
    await callback.message.edit_reply_markup(markup)


# Уровень 2 - информация о выбранном курсе
async def item_info_admin_menu(callback: Union[types.Message, types.CallbackQuery], category, item_id, **kwargs):
    if isinstance(callback, types.CallbackQuery):
        markup = await inline_admin.item_info(category, item_id)
        await callback.message.edit_reply_markup(markup)

    if isinstance(callback, types.Message):
        markup = await inline_admin.item_info(category, item_id)
        await callback.edit_reply_markup(markup)


# Уровень 3 - выбор поля для редактирования
async def update_item_admin_menu(callback: types.CallbackQuery, category, item_id, **kwargs):
    markup = await inline_admin.update_item_menu(category, item_id)
    await callback.message.edit_reply_markup(markup)


# Уровень 4 - редактирование, машина состояний
async def update_item(callback: types.CallbackQuery, state: FSMContext, category, item_id, to_change, **kwargs):
    await callback.message.edit_reply_markup(None)
    async with state.proxy() as data:
        # Передаем необходимую информацию
        data["to_change"] = to_change
        data["item_id"] = item_id
        data["category"] = category
        data["message"] = callback.message

        item = db.get_course(item_id)
        await callback.message.edit_text(messages.make_ask_for_update_course(item[int(to_change)]))
        await FSMUpdateItem.new_value.set()


# Уровень 4 - обновление курса
async def on_update_item(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию
        to_change = data["to_change"]
        item_id = data["item_id"]
        category = data["category"]
        msg = data["message"]
        new_value = validation.validate(message.text)  # Здесь будет валидация, пока заглушка

        if db.update_course(to_change, item_id, new_value):
            item = db.get_course(item_id)
            await msg.edit_text(messages.make_item_info(item, updated=True))
            await item_info_admin_menu(msg, category, item_id)
            try:
                await message.delete()
            except MessageCantBeDeleted:
                pass
        else:
            await bot.send_message(message.from_user.id, "Что-то пошло не так")
        await state.finish()


# Навигация по меню
async def admin_navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    # Достаем инфу из колбека
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')
    to_change = callback_data.get('to_change')

    match current_level:
        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)

        case "1":
            courses = db.get_courses(category)
            await call.message.edit_text("Выберите курс")
            await list_sub_admin_menu(call, category=category, item_id=item_id, courses=courses)

        case "2":
            item = db.get_course(item_id)
            await call.message.edit_text(messages.make_item_info(item, updated=False))
            await item_info_admin_menu(call, item_id=item_id, category=category)

        case "3":
            await update_item_admin_menu(call, item_id=item_id, category=category)

        case "4":
            await update_item(call, category=category, item_id=item_id, to_change=to_change, state=state)


def register_handlers_menu_admin(_dp: Dispatcher):
    _dp.register_callback_query_handler(admin_navigate, inline_admin.menu_cd.filter(), state=None)
    _dp.register_message_handler(on_update_item, state=FSMUpdateItem)
