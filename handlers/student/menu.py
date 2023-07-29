import os
from typing import Union

import tortoise
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, callback_query
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized, \
    MessageNotModified
from aiogram.dispatcher import FSMContext

from tortoise.exceptions import NoValuesFetched
from DB.models import Courses, Users, Administrators
from create_bot import bot, inline_student, validation
from handlers.general.menu import list_categories, check_validate
from static import messages
from dadata import DadataAsync
from create_bot import DADATA_TOKEN, DADATA_SECRET


# Состояния регистрирования информации о студенте
class FSMUpdateStudentInfo(StatesGroup):
    full_name = State()
    study_group = State()
    phone_number = State()
    date_of_birth = State()
    series_data = State()
    number_data = State()
    passport_date = State()
    passport_issued = State()
    department_code = State()
    place_of_registration = State()


# Состояние изменения поля студента
class FSMUpdateUser(StatesGroup):
    new_value = State()


# Уровень 1
async def level_1(callback: Union[types.Message, types.CallbackQuery], category, offset=0, **kwargs):
    match category:

        case "1":  # Открытые курсы
            courses = await Courses.filter(status=int(category)).offset(int(offset)).limit(5)
            print(Courses.filter(status=int(category)).offset(int(offset)).limit(5).sql())
            end_list = True if len(courses) < 5 else False
            await callback.message.edit_text("Выберите курс")
            markup = await inline_student.category_keyboard(category, courses=courses, offset=offset, end_list=end_list)
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
async def info_edit_markup(callback: Union[types.Message, types.CallbackQuery], category, item_id, offset, **kwargs):
    user = await Users.get(id=callback.from_user.id)
    is_sub = await user.courses.filter(id=item_id).exists()

    if isinstance(callback, types.CallbackQuery):
        markup = await inline_student.item_info(category, item_id, int(is_sub), int(offset))
        await callback.message.edit_reply_markup(markup)

    if isinstance(callback, types.Message):
        markup = await inline_student.item_info(category, item_id, int(is_sub), int(offset))
        await callback.edit_reply_markup(markup)


# Уровень 2
async def level_2(callback: types.CallbackQuery, category, state: FSMContext, item_id=0, offset=0,
                  **kwargs):
    if str(category) in "12":
        item = await Courses.get(id=item_id)
        await callback.message.edit_text(messages.make_item_info(item, updated=False))
        await info_edit_markup(callback, category, item_id, offset)
    else:
        user = await Users.get(id=callback.from_user.id)
        if user.full_name is None:
            await callback.message.edit_text(messages.ask_for_update_user_info % ("1", "ФИО", "'Иванов Иван Иванович'"))
            async with state.proxy() as data:
                # Передаем необходимую информацию
                data["category"] = category
                data["call"] = callback
                await FSMUpdateStudentInfo.full_name.set()
        else:
            markup = await inline_student.update_user_info(category, item_id)
            await callback.message.edit_reply_markup(markup)


# Уровень 3

async def level_3(callback: types.CallbackQuery, category, item_id, is_sub, state: FSMContext, offset, change,
                  **kwargs):
    if change == "0":
        await sub_to_course(callback, category, item_id, is_sub, offset)
    else:
        await callback.message.edit_reply_markup(None)

        async with state.proxy() as data:
            # Передаем необходимую информацию
            data["change"] = change
            data["category"] = category
            data["call"] = callback

            item = await Users.get(id=callback.from_user.id)
            await callback.message.edit_text(messages.make_ask_for_update(item[int(change)]))
            await FSMUpdateUser.new_value.set()


async def on_update_user(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:

        # Забираем необходимую информацию
        change = data["change"]
        category = data["category"]
        call = data["call"]
        new_value = message.text

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # # Валидация
        # if change in "34":
        #     code = await validation.val_digit(new_value)
        #     example = "1100"
        # elif change == "5":
        #     code = await validation.val_fio(new_value)
        #     example = "Иванов Иван Иванович"
        # elif change in "16":
        #     code = await validation.val_mix(new_value)
        #     example = "Какой-то текст..."
        # elif change == "2":
        #     code = await validation.val_schedule(new_value)
        #     example = "21.07 - 10:10-11:40"
        # else:
        #     code = await validation.val_bool(new_value)
        #     example = "1"
        #     if new_value == '0':
        #         new_value = False

        # # Проверка полученного кода
        # if code != 200:
        #     await check_validate(call, message, code, example)
        #     return

        # Изменение курса, если сюда пришло, значит проблем нет
        user = await Users.get(id=message.from_user.id)
        user[int(change)] = new_value
        print("new_val", user[int(change)])

        try:
            await user.save()
            await level_1(call, category=category)
        except:
            await bot.send_message(message.from_user.id, messages.went_wrong)
        await state.finish()

        try:
            await message.delete()
        except MessageCantBeDeleted:
            pass


# Уровень 3 - подписка/отписка
async def sub_to_course(callback: types.CallbackQuery, category, item_id, is_sub, offset, **kwargs):
    print("offset - ", offset)
    user = await Users.get(id=callback.from_user.id)

    if user.full_name is None or user.full_name == '':
        await level_1(callback, category="3", offset=int(offset))
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
    await info_edit_markup(callback, category, item_id, int(offset))


# Обработка отмены, выход из состояния и возврат в меню
async def check_cancel_update(call: types.CallbackQuery, message: types.Message, state: FSMContext, category):
    try:
        await level_1(call, category=category)
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
            messages.ask_for_update_user_info % ("5", "Серия паспорта", "'1010'"))
        await FSMUpdateStudentInfo.next()


async def series_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["pseries"] = int(new_value.replace(' ', ''))

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_passSeries(new_value.replace(' ', ''))

        if code != 200:
            await check_validate(call, message, code, "'1010'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("6", "Номер паспорта", "'541222'"))
        await FSMUpdateStudentInfo.next()


async def number_set(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        # Забираем необходимую информацию на случай отмены
        category = data["category"]
        call = data["call"]
        new_value = message.text
        # И кладем новую
        data["pnumber"] = int(new_value.replace(' ', ''))

        # Обработка отмены
        if message.text.lower() == 'отмена':
            await check_cancel_update(call, message, state, category)
            return

        # Обработка ошибки валидации
        code = await validation.val_passnumber(new_value.replace(' ', ''))

        if code != 200:
            await check_validate(call, message, code, "'541222'")
            return

        await message.delete()
        await call.message.edit_text(messages.ask_for_update_user_info % ("7", "Дата выдачи паспорта", "'YYYY-MM-DD'"))
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
        await call.message.edit_text(messages.ask_for_update_user_info % ("8", "Кем выдан паспорт", "'Отделением ...'"))
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
        await call.message.edit_text(messages.ask_for_update_user_info % ("9", "Код паспорта", "'111-222'"))
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
        await call.message.edit_text(
            messages.ask_for_update_user_info % ("10", "Место регистрации", "'Приморский край, г.Владивосток, "
                                                                            "ул. Ленина 17, кв 5'"))
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
        async with DadataAsync(DADATA_TOKEN, DADATA_SECRET) as dadata:
            ans = await dadata.clean(name="address", source=message.text)
            print(ans["result"])
            print(ans["qc"])

        match ans["qc"]:
            case 0:
                pass
            case 1:
                await check_validate(call, message, "Неверный адрес", "'Приморский край, г.Владивосток, ул. Гоголя 17 "
                                                                      "кв 5'")
                return
            case 3:
                await check_validate(call, message, "Неверный адрес", "'Приморский край, г.Владивосток, ул. Гоголя 17 "
                                                                      "кв 5'")
                return

        # Забираем инфу о пользователе
        full_name = data["full_name"]
        group = data["group"]
        phone = data["phone"]
        birth = data["birth"]
        series = data["pseries"]
        number = data["pnumber"]
        pdate = data["pdate"]
        issued = data["issued"]
        dcode = data["dcode"]
        reg_place = ans["result"]

        # Сохраняем пользователя
        try:
            user = await Users.get(id=message.from_user.id)
            user.full_name = full_name
            user.study_group = group
            user.phone_number = phone
            user.date_of_birth = birth
            user.passport_series = series
            user.passport_number = number
            user.passport_date = pdate
            user.passport_issued = issued
            user.reg_place = reg_place
            user.department_code = dcode
            await user.save()
        except NoValuesFetched as e:
            raise e

        try:
            await message.delete()
        except:
            pass

        await level_1(call, category=category)
        await state.finish()


# Навигация
async def student_navigate(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    # Проверка админа на случай наделения пользователя правами
    if await Administrators.exists(id=call.from_user.id):
        await call.message.edit_text("Вы стали админом, авторизуйтесь - /start, затем вызовите новое меню")
        return

    current_level = callback_data.get('level')  # Текущий уровень меню.
    category = callback_data.get('category')  # Текущая категория.
    item_id = callback_data.get('item_id')  # Id выбранного курса (необходимо для уровней 2,3,4).
    is_sub = callback_data.get('sub')  # Флаг показывающий состояние подписки на курс
    offset = callback_data.get('offset')  # Сдвиг по списку курсов в бд
    change = callback_data.get('change')  # Номер поля для изменения

    match current_level:

        case "0":
            await call.message.edit_text("Выберите пункт")
            await list_categories(call)

        case "1":
            await level_1(call, category=category, item_id=item_id, offset=offset)

        case "2":
            await level_2(call, item_id=item_id, category=category, state=state, offset=offset)

        case "3":
            await level_3(call, category=category, item_id=item_id, change=change, state=state, is_sub=is_sub,
                          offset=offset)


def register_handlers_menu_student(_dp: Dispatcher):
    _dp.register_callback_query_handler(student_navigate, inline_student.menu_cd.filter(), state=None)

    _dp.register_message_handler(fullname_set, state=FSMUpdateStudentInfo.full_name)
    _dp.register_message_handler(group_set, state=FSMUpdateStudentInfo.study_group)
    _dp.register_message_handler(phone_set, state=FSMUpdateStudentInfo.phone_number)
    _dp.register_message_handler(birth_set, state=FSMUpdateStudentInfo.date_of_birth)
    _dp.register_message_handler(series_set, state=FSMUpdateStudentInfo.series_data)
    _dp.register_message_handler(number_set, state=FSMUpdateStudentInfo.number_data)
    _dp.register_message_handler(pdate_set, state=FSMUpdateStudentInfo.passport_date)
    _dp.register_message_handler(dcode_set, state=FSMUpdateStudentInfo.department_code)
    _dp.register_message_handler(issued_set, state=FSMUpdateStudentInfo.passport_issued)
    _dp.register_message_handler(reg_set, state=FSMUpdateStudentInfo.place_of_registration)

    _dp.register_message_handler(on_update_user, state=FSMUpdateUser.new_value)
