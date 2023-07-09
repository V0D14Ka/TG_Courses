from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized
from aiogram.dispatcher import FSMContext

from DB.models import Users, Administrators
from create_bot import bot
from static import messages


class FSMAdmin(StatesGroup):
    password = State()
    message = State()


async def commands_start(message: types.Message):
    try:
        if await Administrators.exists(id=message.from_user.id):
            admin = await Administrators.get(id=message.from_user.id)
            if admin.is_active:
                await bot.send_message(message.from_user.id,
                                       messages.already_authenticated)
            else:
                # Admin authentication logic
                await FSMAdmin.password.set()
                await bot.send_message(message.from_user.id,
                                       messages.ask_for_password)
        else:
            if not await Users.exists(id=message.from_user.id):
                await Users.create(
                    id=message.from_user.id
                )
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


# Проверка введенного админом пароля
async def check_password(message: types.Message, state: FSMContext):

    res = await Administrators.get(id=message.from_user.id)
    if res.password == message.text:
        res.is_active = True
        await res.save()
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
