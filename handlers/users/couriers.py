import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from filters.users_filters import IsCourierCallback, IsCourierMessage
from keyboards.inline.callback_datas import order_is_delivered
from loader import dp, db, bot
from utils.check_states import reset_state
from utils.emoji import success_em, error_em


@dp.message_handler(IsCourierMessage(), commands=['im_at_work'], state=['*'])
async def im_at_work(message: types.Message):
    """Ставим статус на работе"""
    await db.im_at_work_courier(message.from_user.id, 'true')
    await message.answer(f'{success_em} Теперь Вы будете получать заказы')


@dp.message_handler(IsCourierMessage(), commands=['im_at_home'], state=['*'])
async def im_at_home(message: types.Message):
    """Ставим статус дома"""
    await db.im_at_work_courier(message.from_user.id, 'false')
    await message.answer(f'{error_em} Теперь Вы не будете получать заказы')


@dp.message_handler(IsCourierMessage(), commands=['all_ready_orders'], state=["*"])
async def get_active_orders(message: types.Message, state: FSMContext):
    """Показать список всех заказов, готовых к доставке"""
    await reset_state(state, message)
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
                                                                                  user_id=order[
                                                                                      'order_user_telegram_id'])
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
        try:
            await bot.send_message(user_id,
                                   f'Ваш заказ № {order_id} доставлен.\n'
                                   f'Приятного аппетита!')
            await call.message.answer(f'{success_em} Заказ № {order_id} доставлен!')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f'Не удалось отправить уведомление пользователю.\n'
                                      f'Заказ отмечен как доставлен.')
    else:
        await call.message.answer('Заказ уже отмечен как доставлен.')
