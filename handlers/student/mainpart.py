from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageCantBeDeleted, CantInitiateConversation, BotBlocked, Unauthorized

from create_bot import db, bot
from static import messages


async def commands_start(message: types.Message):
    if not db.is_user_exist(message.from_user.id):
        db.add_user(message.from_user.id)
        db.save()
    mesg = messages.welcome_mesg if message.get_command() == '/start' else messages.help_mesg

    try:
        await bot.send_message(message.from_user.id, mesg)  # , reply_markup=kb_client
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


def register_handlers_student(_dp: Dispatcher):
    _dp.register_message_handler(commands_start, commands=['start', 'help'])
