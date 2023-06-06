from create_bot import db
from keyboard import InlineAdmin, InlineStudent

inline_admin = InlineAdmin(db)
inline_student = InlineStudent(db)


async def get_menu(is_admin):
    if is_admin:
        markup = await inline_admin.menu_keyboard(is_admin)
    else:
        markup = await inline_student.menu_keyboard()

    return markup


async def get_category_keyboard(is_admin, category):
    if is_admin:
        markup = await inline_admin.category_keyboard(is_admin, category)
    else:
        markup = await inline_student.category_keyboard(category)

    return markup


async def get_item_keyboard(is_admin, category, item_id):
    if is_admin:
        markup = await inline_admin.item_info(is_admin, category, item_id)
    else:
        markup = await inline_student.item_info(category, item_id)

    return markup
