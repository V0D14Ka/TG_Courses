from typing import Union

import tortoise
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, callback_query
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized, \
    MessageNotModified
from aiogram.dispatcher import FSMContext

from tortoise.exceptions import NoValuesFetched
from DB.models import Courses, Users, admin_pydantic, student_pydantic
from create_bot import bot, inline_student, validation
from handlers.general.menu import list_categories, check_validate
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
            courses = await Courses.filter(status=int(category))
            await callback.message.edit_text("Выберите курс")
            markup = await inline_student.category_keyboard(category, courses=courses)
            await callback.message.edit_reply_markup(markup)

        case "2":  # Мои курсы
            user = await Users.get(id=callback.from_user.id)
            courses = await user.courses.all()
            await callback.message.edit_text("Выберите курс")
            markup = await inline_student.category_keyboard(category, courses=courses)
            await callback.message.edit_reply_markup(markup)

        case "3":  # Информация о себе
            user = await Users.get(id=callback.from_user.id)

            if user.full_name is None or user.full_name == '':
                message = "Вы еще не заполнили информацию о себе"
                await callback.message.edit_text(message)
                markup = await inline_student.category_keyboard(category, empty_info=True)
            else:
                message = await messages.make_user_info(user, updated=False)
                await callback.message.edit_text(message)
                markup = await inline_student.category_keyboard(category, user_info=user)

            await callback.message.edit_reply_markup(markup)


# Корректная выдача клавиатуры уровня 2
async def info_edit_markup(callback: Union[types.Message, types.CallbackQuery], category, item_id, **kwargs):
    user = await Users.get(id=callback.from_user.id)
    is_sub = await user.courses.filter(id=item_id).exists()

    if isinstance(callback, types.CallbackQuery):
        markup = await inline_student.item_info(category, item_id, int(is_sub))
        await callback.message.edit_reply_markup(markup)

    if isinstance(callback, types.Message):
        markup = await inline_student.item_info(category, item_id, int(is_sub))
        await callback.edit_reply_markup(markup)


# Уровень 2
async def sublist_func_student(callback: types.CallbackQuery, category, state: FSMContext, item_id=0, **kwargs):
    if str(category) in "12":
        item = await Courses.get(id=item_id)
        await callback.message.edit_text(messages.make_item_info(item, updated=False))
        await info_edit_markup(callback, category, item_id)
    else:
        await callback.message.edit_text(messages.ask_for_update_user_info % ("1", "ФИО", "'Иванов Иван Иванович'"))
        async with state.proxy() as data:
            # Передаем необходимую информацию
            data["category"] = category
            data["call"] = callback
            await FSMUpdateStudentInfo.full_name.set()


# Уровень 3 - подписка/отписка
async def sub_to_course(callback: types.CallbackQuery, category, item_id, is_sub, **kwargs):
    user = await Users.get(id=callback.from_user.id)

    if user.full_name is None or user.full_name == '':
        await list_func_student(callback, category="3")
        return

    course = await Courses.get(id=item_id)
    if int(is_sub) == 0:
        await user.courses.add(course)
        await user.save()
        await callback.answer("Вы успешно записались на курс!", show_alert=True)
    elif int(is_sub) == 1:
        await user.courses.remove(course)
        await user.save()
        await callback.answer("Вы отменили запись на курс.", show_alert=True)

    await callback.answer("Уведомление", show_alert=True)
    await info_edit_markup(callback, category, item_id)


# Обработка отмены, выход из состояния и возврат в меню
async def check_cancel_update(call: types.CallbackQuery, message: types.Message, state: FSMContext, category):
    try:
        await list_func_student(call, category=category)
        await message.delete()
        await state.finish()
    except MessageCantBeDeleted:
        pass
    return True


# Далее FSM
async def fullname_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["full_name"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_fio(new_value)

        if code != 200:
            await check_validate(call, message, code, "'Иванов Иван Иванович'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("2", "Номер группы", "'Б9999-11.11.11'"))
        await FSMUpdateStudentInfo.next()


async def group_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["group"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_mix(new_value)

        if code != 200:
            await check_validate(call, message, code, "'Б9999-11.11.11'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("3", "Номер телефона", "'89990001111'"))
        await FSMUpdateStudentInfo.next()


async def phone_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["phone"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_phone(new_value)

        if code != 200:
            await check_validate(call, message, code, "'89990001111'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("4", "Дату рождения", "'YYYY-MM-DD'"))
        await FSMUpdateStudentInfo.next()


async def birth_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["birth"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_date(new_value)

        if code != 200:
            await check_validate(call, message, code, "'YYYY-MM-DD'")
            return

        await message.delete()
        await call.message.edit_text(
            messages.ask_for_update_user_info % ("5", "Серия и номер паспорта", "'1010 123456'"))
        await FSMUpdateStudentInfo.next()


async def pdata_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["pdata"] = int(new_value.replace(' ', ''))

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_pass(new_value.replace(' ', ''))

        if code != 200:
            await check_validate(call, message, code, "'1010 123456'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("6", "Дата выдачи паспорта", "'YYYY-MM-DD'"))
        await FSMUpdateStudentInfo.next()


async def pdate_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["pdate"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_date(new_value)

        if code != 200:
            await check_validate(call, message, code, "'YYYY-MM-DD'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("7", "Кем выдан паспорт", "'Отделением ...'"))
        await FSMUpdateStudentInfo.next()


async def issued_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["issued"] = new_value

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_text(new_value)

        if code != 200:
            await check_validate(call, message, code, "'Отделением ...'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("8", "Код паспорта", "'111-222'"))
        await FSMUpdateStudentInfo.next()


async def dcode_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["dcode"] = new_value.replace('-', '')

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_passcode(new_value)

        if code != 200:
            await check_validate(call, message, code, "'111-222'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("9", "Место регистрации", "'Владивосток, "
                                                                                                    "ул.Ленина 1'"))
        await FSMUpdateStudentInfo.next()


async def reg_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_mix(message.text.replace(' ', ''))

        if code != 200:
            await check_validate(call, message, code, "'Владивосток, ул.Ленина 1'")
            return

        # Забираем инфу о пользователе
        full_name = data["full_name"]
        group = data["group"]
        phone = data["phone"]
        birth = data["birth"]
        pdata = data["pdata"]
        pdate = data["pdate"]
        issued = data["issued"]
        dcode = data["dcode"]
        reg_place = message.text

        # Сохраняем пользователя
        try:
            user = await Users.get(id=message.from_user.id)
            user.full_name = full_name
            user.study_group = group
            user.phone_number = phone
            user.date_of_birth = birth
            user.passport_data = pdata
            user.passport_date = pdate
            user.passport_issued = issued
            user.place_of_registration = reg_place
            user.department_code = dcode
            await user.save()
        except NoValuesFetched as e:
            raise e

        try:
            await message.delete()
        except:
            pass

        await list_func_student(call, category=category)
        await FSMUpdateStudentInfo.next()
        await state.finish()


# Навигация
async def student_navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    item_id = callback_data.get('item_id')
    is_sub = callback_data.get('sub')

    match current_level:
        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)
        case "1":
            await list_func_student(call, category=category, item_id=item_id)
        case "2":
            await sublist_func_student(call, item_id=item_id, category=category, state=state)
        case "3":
            await sub_to_course(call, category=category, item_id=item_id, is_sub=is_sub)


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
