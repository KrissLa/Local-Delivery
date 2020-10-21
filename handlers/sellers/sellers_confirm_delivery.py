from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import IsSellerCallback
from keyboards.inline.callback_datas import order_is_delivered, reviev_order_data
from loader import dp, db, bot
from utils.emoji import success_em


@dp.callback_query_handler(IsSellerCallback(), order_is_delivered.filter())
async def confirm_delivery_courier(call: CallbackQuery, callback_data: dict):
    """Продавец подтверждает выдачу"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    await db.update_order_status(order_id, "Выполнен")
    await db.update_order_delivered_at(order_id)
    await db.order_is_delivered(user_id)
    await call.message.answer(f'{success_em}Заказ № {order_id} выдан!')
    await bot.send_message(user_id,
                           f'{success_em} Ваш заказ № {order_id} выдан.\n'
                           f'Приятного аппетита!',
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [
                                   InlineKeyboardButton(
                                       text='Написать отзыв',
                                       callback_data=reviev_order_data.new(order_id=order_id)
                                   )
                               ]
                           ]))
