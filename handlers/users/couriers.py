from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from filters.users_filters import IsCourierCallback
from keyboards.inline.callback_datas import order_is_delivered
from loader import dp, db, bot


@dp.message_handler(commands=['all_ready_orders'], state=["*"])
async def get_active_orders(message: types.Message, state: FSMContext):
    """Показать список всех заказов, готовых к доставке"""
    await state.finish()
    all_waitings_orders = await db.get_all_ready_orders_for_courier(message.from_user.id)
    if all_waitings_orders:
        for order in all_waitings_orders:
            await message.answer(f'Заказ № {order["order_id"]}.\n'
                                 f'{order["order_info"]}'
                                 f'Адрес: {order["order_local_object_name"]},\n'
                                 f'{order["delivery_address"]}\n'
                                 f'Доставить в {order["deliver_to"].strftime("%H:%M")}\n'
                                 f'Стоимость заказа: {order["order_price"]} руб',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Заказ доставлен!',
                                             callback_data=order_is_delivered.new(order_id=order["order_id"],
                                                                                  user_id=order['order_user_telegram_id'])
                                         )
                                     ]
                                 ]))
    else:
        await message.answer('Нет готовых к доставке заказов.')


@dp.message_handler(commands=['my_orders'], state=['*'])
async def get_my_orders(message: types.Message, state: FSMContext):
    """Список заказов закрепленных за курьером"""
    await state.finish()
    couriers_orders = await db.get_all_waiting_orders_for_courier(message.from_user.id)
    if couriers_orders:
        await message.answer('Вам назначены следующие заказы:')
        for order in couriers_orders:
            await message.answer(f'Заказ № {order["order_id"]}.\n'
                                 f'{order["order_info"]}'
                                 f'Адрес: {order["order_local_object_name"]},\n'
                                 f'{order["delivery_address"]}\n'
                                 f'Доставить в {order["deliver_to"].strftime("%H:%M")}\n'
                                 f'Статус заказ: {order["order_status"]}\n'
                                 f'Стоимость заказа: {order["order_price"]} руб')
    else:
        await message.answer('Пока Вам не назначили заказов.')


@dp.callback_query_handler(IsCourierCallback(), order_is_delivered.filter())
async def confirm_delivery_courier(call: CallbackQuery, callback_data: dict):
    """Курьер подтверждает доставку"""
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    if await db.order_is_delivered(order_id, user_id):
        await call.message.answer(f'Заказ № {order_id} доставлен!')
        await bot.send_message(user_id,
                               f'Ваш заказ № {order_id} доставлен.\n'
                               f'Приятного аппетита!')
    else:
        await call.message.answer('Заказ уже отмечен как доставлен.')
