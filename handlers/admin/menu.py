from typing import Union, List

from utils.schedule import sort_strings_by_datetime
from . import signals
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import message
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageNotModified
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink
from tortoise.signals import post_save

from DB.models import Courses, Administrators, Users
from create_bot import bot, inline_admin, validation
from handlers.general.menu import list_categories, check_validate
from static import messages

from tortoise.exceptions import NoValuesFetched

from tasks.tasks import on_update_course_task


# Класс состояния для редактирования
class FSMUpdateItem(StatesGroup):
    new_value = State()


# Уровень 1 - курсы по выбранной категории
async def level_1(callback: types.CallbackQuery, category, courses, end_list, offset, **kwargs):
    markup = await inline_admin.category_keyboard(category, courses, offset, end_list)
    await callback.message.edit_reply_markup(markup)


# Уровень 2 - информация о выбранном курсе
async def level_2(call, message, category, item_id, offset):
    await call.edit_text(message)
    await item_info_admin_menu(call, category, item_id, offset)


async def item_info_admin_menu(callback: Union[types.Message, types.CallbackQuery], category, item_id, offset, **kwargs):
    if isinstance(callback, types.CallbackQuery):
        markup = await inline_admin.item_info(category, item_id, offset)
        await callback.message.edit_reply_markup(markup)

    if isinstance(callback, types.Message):
        markup = await inline_admin.item_info(category, item_id, offset)
        await callback.edit_reply_markup(markup)


# Уровень 3 - выбор поля для редактирования
async def level_3(callback: types.CallbackQuery, category, item_id, flag, offset, **kwargs):

    if int(flag) == 1:
        # Выбрано "Записавшиеся"
        users = await Users.filter(courses=item_id).values("id", "full_name", "study_group")

        if len(users) != 0:
            ans = ""
            i = 1
            for user in users:
                ans += (f'{i}.' + hlink(str(user["full_name"]), f"tg://openmessage?user_id={user['id']}")
                                                 + ", " + str(user["study_group"]) + '.\n')
                i += 1
            await callback.message.edit_text(ans, parse_mode=types.ParseMode.HTML)
        else:
            await callback.message.edit_text("Список пуст :(")

        markup = await inline_admin.back_markup(category, item_id, offset)
        await callback.message.edit_reply_markup(markup)

    else:
        # Меню выбора поля для редактирования
        markup = await inline_admin.update_item_menu(category, item_id, offset)
        await callback.message.edit_reply_markup(markup)


# Уровень 4 - редактирование, машина состояний
async def level_4(callback: types.CallbackQuery, state: FSMContext, category, item_id, to_change, offset, **kwargs):
    await callback.message.edit_reply_markup(None)

    async with state.proxy() as data:
        # Передаем необходимую информацию
        data["to_change"] = to_change
        data["item_id"] = item_id
        data["category"] = category
        data["call"] = callback
        data["offset"] = offset

        item = await Courses.get(id=item_id)
        await callback.message.edit_text(messages.make_ask_for_update(item[int(to_change)]))
        await FSMUpdateItem.new_value.set()


# Обработка отмены, выход из состояния и возврат в меню
async def check_cancel_update(call, message, state, category, item_id, offset):
    item = await Courses.get(id=item_id)
    try:
        await level_2(call.message, messages.make_item_info(item, updated=False), category, item_id, offset)
        await message.delete()
        await state.finish()
    except MessageCantBeDeleted:
        pass
    return


# Уровень 4.1 - обновление курса
async def on_update_item(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:

        # Забираем необходимую информацию
        to_change = data["to_change"]
        item_id = data["item_id"]
        category = data["category"]
        call = data["call"]
        offset = data["offset"]
        new_value = message.text

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category, item_id, offset)
            return

        # Валидация
        if to_change in "34":
            code = await validation.val_digit(new_value)
            example = "1100"
        elif to_change == "5":
            code = await validation.val_fio(new_value)
            example = "Иванов Иван Иванович"
        elif to_change in "16":
            code = await validation.val_mix(new_value)
            example = "Какой-то текст..."
        elif to_change == "2":
            code = await validation.val_schedule(new_value)
            if code == 200:
                new_value = await sort_strings_by_datetime(new_value.split(";"))
            example = '''Расписание в строчку с разделителем ';' "21.07.2023 10:10-11:40;25.07.2023 11:50-13:20..."'''
        else:
            code = await validation.val_bool(new_value)
            example = "1"
            if new_value == '0':
                new_value = False

        # Проверка полученного кода
        if code != 200:
            await check_validate(call, message, code, example)
            return

        # Изменение курса, если сюда пришло, значит проблем нет
        item = await Courses.get(id=item_id)
        item[int(to_change)] = new_value
        print("new_val", item[int(to_change)])

        try:
        # await Courses.create(status=True, title="test", schedule="10.08.2023 11:50-13:20")
            await item.save()
            item = await Courses.get(id=item_id)
            await level_2(call.message, messages.make_item_info(item, updated=True), category, item_id, offset=offset)

        except:
            await bot.send_message(message.from_user.id, messages.went_wrong)
        await state.finish()

        try:
            await message.delete()
        except MessageCantBeDeleted:
            pass


# Навигация по меню
async def admin_navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    print(callback_data)
    # Проверка админа на случай отзыва прав
    if not await Administrators.exists(id=call.from_user.id, is_active=True):
        await call.message.edit_text("У вас больше нет прав пользоваться этим меню, вызовите новое - /menu")
        return

    # Достаем информацию из колбека
    current_level = callback_data.get('level')  # Текущий уровень меню.
    category = callback_data.get('category')   # Текущая категория.
    item_id = callback_data.get('item_id')  # Id выбранного курса (необходимо для уровней 2,3,4).
    to_change = callback_data.get('to_change')  # Номер поля выбранного курса для изменения (необходимо для уровня 4).
    flag = callback_data.get('flag')  # Флаг показывает какой пункт меню был выбран (необходимо для уровня 3).
    offset = callback_data.get('offset')  # Сдвиг по списку курсов в бд

    # Смотрим какой уровень был вызван
    match current_level:

        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)

        case "1":
            courses = await Courses.filter(status=int(category)).offset(int(offset)).limit(5)
            end_list = True if len(courses) < 5 else False

            await call.message.edit_text("Выберите курс")
            await level_1(call, category=category, courses=courses, offset=offset, end_list=end_list)

        case "2":
            item = await Courses.get(id=item_id)
            await level_2(call.message, messages.make_item_info(item, updated=False), category, item_id, offset)

        case "3":
            await level_3(call, category=category, item_id=item_id, flag=flag, offset=offset)

        case "4":
            await level_4(call, category=category, item_id=item_id, to_change=to_change, state=state, offset=offset)


def register_handlers_menu_admin(_dp: Dispatcher):
    _dp.register_callback_query_handler(admin_navigate, inline_admin.menu_cd.filter(), state=None)
    _dp.register_message_handler(on_update_item, state=FSMUpdateItem)
