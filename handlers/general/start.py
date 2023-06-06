from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from create_bot import db, bot
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

    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass
    await bot.send_message(message.from_user.id, text=answer)
    await state.finish()


def register_handlers_start(_dp: Dispatcher):
    _dp.register_message_handler(commands_start, commands=['start', 'help'], state=None)
    _dp.register_message_handler(check_password, state=FSMAdmin.password)
