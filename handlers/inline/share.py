from aiogram import types
from aiogram.types import InputMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp


@dp.inline_handler()
async def shre_query(query: types.InlineQuery):
    """Передаем реф ссылку другу"""

    bot_user = await dp.bot.get_me()

    await query.answer(
        results=[types.InlineQueryResultArticle(
            id="unknown",
            title="Отправить приглашение",
            input_message_content=InputMessageContent(
                message_text=f"Привет! Приглашаю тебя в {bot_user.full_name}. Там можно заказывать еду)\n"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Перейти к боту',
                                             url=f'http://t.me/{bot_user.username}?start={query.from_user.id}')
                    ]
                ]
            )

        )])
