import math

import emoji
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.parts import paginate

from keyboards.inline.callback_datas import page_call_data


async def add_pagination(buttons_list, page):
    """Добавляем пагинацию к клавиатуре"""
    last_page = math.ceil(len(buttons_list) / 10) - 1
    page_data = paginate(buttons_list, page=page, limit=10)
    if page == 0:
        page_data.append([
            InlineKeyboardButton(text=emoji.emojize(f':arrow_right:', use_aliases=True),
                                 callback_data=page_call_data.new(page=1))
        ])
    elif page == last_page:
        page_data.append([
            InlineKeyboardButton(text=emoji.emojize(f':arrow_left:', use_aliases=True),
                                 callback_data=page_call_data.new(page=last_page - 1))
        ])
    else:
        page_data.append([
            InlineKeyboardButton(text=emoji.emojize(f':arrow_left:', use_aliases=True),
                                 callback_data=page_call_data.new(page=page - 1)),
            InlineKeyboardButton(text=emoji.emojize(f':arrow_right:', use_aliases=True),
                                 callback_data=page_call_data.new(page=page + 1)),
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=page_data)
    return keyboard
