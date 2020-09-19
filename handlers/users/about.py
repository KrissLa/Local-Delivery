from aiogram import types

from loader import dp, db
from utils.temp_orders_list import get_objects_list_message


@dp.message_handler(text="О сервисе")
async def show_about(message: types.Message):
    """Отправляем инфу о компании"""
    about = await db.get_about()
    list_of_object = await db.get_objects()
    objects = await get_objects_list_message(list_of_object)
    await message.answer(f'{about}\n\n'
                         f'Адреса, где работает доставка:\n\n'
                         f'{objects}')
