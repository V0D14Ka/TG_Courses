from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext
from create_bot import db, bot, inline_kb
from static import messages


class FSMAdmin(StatesGroup):
    password = State()
    message = State()


async def commands_start(message: types.Message):
    try:
        if db.is_admin_exist(message.from_user.id):
            print("is Admin")
            if db.is_admin_active(message.from_user.id):
                print("Admin is active")
                await bot.send_message(message.from_user.id,
                                       messages.already_authenticated)
            else:
                # Admin authentication logic
                await FSMAdmin.password.set()
                await bot.send_message(message.from_user.id,
                                       messages.ask_for_password)
        else:
            if not db.is_user_exist(message.from_user.id):
                db.reg_user(message.from_user.id)
                db.save()
            msg = messages.welcome_mesg if message.get_command() == '/start' else messages.help_mesg

            await bot.send_message(message.from_user.id, msg)

        try:
            await message.delete()
        except MessageCantBeDeleted:
            pass

    except CantInitiateConversation:
        await message.reply(messages.cant_initiate_conversation)
    except BotBlocked:
        await message.reply(messages.bot_blocked)
    except Unauthorized:
        await message.reply(messages.unauthorized)


async def check_password(message: types.Message, state: FSMContext):
    res = db.check_admin_password(message.from_user.id, message.text)
    if res:
        db.make_admin_active(message.from_user.id)
    answer = "Успешно, используйте /menu" if res else "Неверный пароль"

    await message.delete()
    await bot.send_message(message.from_user.id, text=answer)
    await state.finish()


async def show_menu(message: types.Message):
    await list_categories(message)


async def list_categories(message: Union[types.CallbackQuery, types.Message], **kwargs):
    markup = await inline_kb.menu_keyboard(db.is_admin_exist(message.from_user.id))

    if isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)

    if isinstance(message, types.Message):
        await message.answer("Выберите пункт", reply_markup=markup)


async def list_sub(callback: types.CallbackQuery, category, is_admin,  **kwargs):
    markup = await inline_kb.category_keyboard(is_admin, category)
    await callback.message.edit_reply_markup(markup)


async def item_info(callback: types.CallbackQuery, category, is_admin, item_id, **kwargs):
    markup = await inline_kb.item_info(is_admin, category, item_id)
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


def register_handlers_general(_dp: Dispatcher):
    _dp.register_message_handler(commands_start, commands=['start', 'help'], state=None)
    _dp.register_message_handler(check_password, state=FSMAdmin.password)
    _dp.register_message_handler(show_menu, commands=['menu'])
    _dp.register_callback_query_handler(navigate, inline_kb.menu_cd.filter())
