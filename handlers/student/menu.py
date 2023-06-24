from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from DB.models import Courses, Users
from create_bot import bot, inline_student
from handlers.general.menu import list_categories
from static import messages


# Состояния редактирования информации о себе
class FSMUpdateStudentInfo(StatesGroup):
    full_name = State()
    study_group = State()
    phone_number = State()
    date_of_birth = State()
    passport_data = State()
    passport_date = State()
    passport_issued = State()
    department_code = State()
    place_of_registration = State()


# Уровень 1
async def list_func_student(callback: Union[types.Message, types.CallbackQuery], category, **kwargs):
    match category:
        case "1":  # Открытые курсы
            courses = await Courses.filter(id=category)
            await callback.message.edit_text("Выберите курс")
            markup = await inline_student.category_keyboard(category, courses=courses)

        case "2":  # Мои курсы
            pass

        case "3":  # Информация о себе
            user = await Users.get(id=callback.from_user.id)

            if user.full_name is not None:
                message = await messages.make_user_info(user, updated=False)
                await callback.message.edit_text(message)
                markup = await inline_student.category_keyboard(category, user_info=user)
            else:
                message = "Вы еще не заполнили информацию о себе"
                await callback.message.edit_text(message)
                markup = await inline_student.category_keyboard(category, empty_info=True)

    await callback.message.edit_reply_markup(markup)


# Корректная выдача клавиатуры уровня 2
async def info_edit_markup(callback: Union[types.Message, types.CallbackQuery], category, item_id, **kwargs):
    if isinstance(callback, types.CallbackQuery):
        markup = await inline_student.item_info(category, item_id)
        await callback.message.edit_reply_markup(markup)

    if isinstance(callback, types.Message):
        markup = await inline_student.item_info(category, item_id)
        await callback.edit_reply_markup(markup)


# Уровень 2
async def sublist_func_student(callback: types.CallbackQuery, category, state: FSMContext, item_id=0, **kwargs):
    match category:
        case "1":  # Детальная информация о курсе
            item = await Courses.get(id=item_id)
            await callback.message.edit_text(messages.make_item_info(item, updated=False))
            await info_edit_markup(callback, category, item_id)
        case "2":  # Детальная информация о курсе
            pass
        case "3":  # Старт редактирования профиля
            await callback.message.edit_text(messages.ask_for_update_user_info % "ФИО")
            async with state.proxy() as data:
                # Передаем необходимую информацию
                data["category"] = category
                data["message"] = callback
                await FSMUpdateStudentInfo.full_name.set()


# Далее FSM
async def fullname_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:

        # Забираем необходимую информацию
        category = data["category"]
        msg = data["message"]
        new_value = message.text
        # И кладем новую
        data["full_name"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            try:
                await list_func_student(msg, category=category)
                await message.delete()
                await state.finish()
            except MessageCantBeDeleted:
                pass
            return

        await message.delete()
        await msg.message.edit_text(messages.ask_for_update_user_info % "Номер группы")
        await FSMUpdateStudentInfo.next()


async def group_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        msg = data["message"]
        new_value = message.text
        # И кладем новую
        data["group"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            try:
                await list_func_student(msg, category=category)
                await message.delete()
                await state.finish()
            except MessageCantBeDeleted:
                pass
            return

        await message.delete()
        await msg.message.edit_text(messages.ask_for_update_user_info % "Номер телефона")
        await FSMUpdateStudentInfo.next()
        await state.finish()


async def phone_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def birth_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def pdata_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def pdate_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def issued_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def dcode_set(message: types.Message, state: FSMContext, **kwargs):
    pass


async def reg_set(message: types.Message, state: FSMContext, **kwargs):
    pass


# Навигация
async def student_navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')

    match current_level:
        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)
        case "1":
            await list_func_student(call, category=category, item_id=item_id)
        case "2":
            await sublist_func_student(call, item_id=item_id, category=category, state=state)


def register_handlers_menu_student(_dp: Dispatcher):
    _dp.register_callback_query_handler(student_navigate, inline_student.menu_cd.filter(), state=None)
    _dp.register_message_handler(fullname_set, state=FSMUpdateStudentInfo.full_name)
    _dp.register_message_handler(group_set, state=FSMUpdateStudentInfo.study_group)
    _dp.register_message_handler(phone_set, state=FSMUpdateStudentInfo.phone_number)
    _dp.register_message_handler(birth_set, state=FSMUpdateStudentInfo.date_of_birth)
    _dp.register_message_handler(pdata_set, state=FSMUpdateStudentInfo.passport_data)
    _dp.register_message_handler(pdate_set, state=FSMUpdateStudentInfo.passport_date)
    _dp.register_message_handler(dcode_set, state=FSMUpdateStudentInfo.department_code)
    _dp.register_message_handler(issued_set, state=FSMUpdateStudentInfo.passport_issued)
    _dp.register_message_handler(reg_set, state=FSMUpdateStudentInfo.place_of_registration)
