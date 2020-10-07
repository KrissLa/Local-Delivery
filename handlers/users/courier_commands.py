from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import IsCourierMessage
from keyboards.inline.callback_datas import order_is_delivered, active_order_cancel_data
from loader import dp, db
from utils.check_states import reset_state
from utils.emoji import success_em, error_em, grey_exclamation_em, blue_diamond_em
from utils.product_list import get_product_list


@dp.message_handler(IsCourierMessage(), commands=['im_at_work'], state=['*'])
async def im_at_work(message: types.Message, state: FSMContext):
    """Ставим статус на работе"""
    await reset_state(state, message)
    await db.im_at_work_courier(message.from_user.id, 'true')
    await message.answer(f'{success_em} Теперь Вы будете получать заказы')


@dp.message_handler(IsCourierMessage(), commands=['im_at_home'], state=['*'])
async def im_at_home(message: types.Message, state: FSMContext):
    """Ставим статус дома"""
    await reset_state(state, message)
    await db.im_at_work_courier(message.from_user.id, 'false')
    await message.answer(f'{error_em} Теперь Вы не будете получать заказы')


@dp.message_handler(IsCourierMessage(), commands=['all_ready_orders'], state=["*"])
async def get_active_orders(message: types.Message, state: FSMContext):
    """Показать список всех заказов, готовых к доставке"""
    await reset_state(state, message)
    all_waitings_orders = await db.get_all_ready_orders_for_courier(message.from_user.id)
    if all_waitings_orders:
        for order in all_waitings_orders:
            await message.answer(f'{grey_exclamation_em}Заказ № {order["order_id"]}.\n'
                                 f'{await get_product_list(order["order_id"])}\n'
                                 f'Адрес: {order["local_object_name"]},\n'
                                 f'{order["order_address"]}\n'
                                 f'Доставить в {order["order_time_for_delivery"].strftime("%H:%M")}\n'
                                 f'Стоимость заказа: {order["order_final_price"]} руб',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text=f'Заказ {order["order_id"]} доставлен!',
                                             callback_data=order_is_delivered.new(order_id=order["order_id"],
                                                                                  user_id=order[
                                                                                      'user_telegram_id'])
                                         )
                                     ],
                                     [
                                         InlineKeyboardButton(
                                             text=f'Отменить заказ {order["order_id"]}',
                                             callback_data=active_order_cancel_data.new(order_id=order['order_id'])
                                         )
                                     ]
                                 ]))
    else:
        await message.answer('Нет готовых к доставке заказов.')


@dp.message_handler(IsCourierMessage(), commands=['my_orders'], state=['*'])
async def get_my_orders(message: types.Message, state: FSMContext):
    """Список заказов закрепленных за курьером"""
    await reset_state(state, message)
    couriers_orders = await db.get_all_waiting_orders_for_courier(message.from_user.id)
    if couriers_orders:
        await message.answer('Вам назначены следующие заказы:')
        for order in couriers_orders:
            await message.answer(f'{blue_diamond_em}Заказ № {order["order_id"]}.\n'
                                 f'{await get_product_list(order["order_id"])}\n'
                                 f'Адрес доставки: {order["local_object_name"]},\n'
                                 f'{order["order_address"]}\n'
                                 f'Доставить в {order["order_time_for_delivery"].strftime("%H:%M")}\n'
                                 f'Статус заказ: {order["order_status"]}\n'
                                 f'Стоимость заказа: {order["order_final_price"]} руб')
    else:
        await message.answer('Пока Вам не назначили заказов.')