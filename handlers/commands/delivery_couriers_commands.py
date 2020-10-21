import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.users_filters import IsDeliveryCourierMessage
from keyboards.inline.inline_keyboards import gen_confirm_order_markup, gen_courier_confirm_markup
from loader import dp, db
from utils.check_states import reset_state, states_for_menu
from utils.emoji import attention_em, blue_diamond_em, success_em, error_em
from utils.product_list import get_delivery_product_list
from utils.temp_orders_list import weekdays


@dp.message_handler(IsDeliveryCourierMessage(), commands=['im_at_work_dc'], state=['*'])
async def im_at_work(message: types.Message, state: FSMContext):
    """Ставим статус на работе"""
    await reset_state(state, message)
    await db.im_at_work_delivery_courier(message.from_user.id, 'true')
    await message.answer(f'{success_em} Теперь Вы будете получать заказы')


@dp.message_handler(IsDeliveryCourierMessage(), commands=['im_at_home_dc'], state=['*'])
async def im_at_home(message: types.Message, state: FSMContext):
    """Ставим статус дома"""
    await reset_state(state, message)
    await db.im_at_work_delivery_courier(message.from_user.id, 'false')
    await message.answer(f'{error_em} Теперь Вы не будете получать заказы')


@dp.message_handler(IsDeliveryCourierMessage(), commands=['confirm_delivery_order'], state=states_for_menu)
@dp.message_handler(IsDeliveryCourierMessage(), commands=['confirm_delivery_order'])
async def take_orders(message: types.Message, state: FSMContext):
    """Список непринятых или измененных заказов"""
    await reset_state(state, message)
    orders = await db.get_accepted_delivery_orders_for_courier(message.from_user.id)
    if orders:
        await message.answer('Список заказов, ожидающих доставки:')
        for order in orders:
            await message.answer(f'{blue_diamond_em}Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Время создания {order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order["delivery_order_status"]}\n'
                                 f'{attention_em} Чтобы подтвердить доставку нажмите '
                                 f'/confirm_delivery_order_{order["delivery_order_id"]}')
    else:
        await message.answer('Нет заказов, ожидающих доставки.')


@dp.message_handler(IsDeliveryCourierMessage(), regexp="confirm_delivery_order_\d+", state=states_for_menu)
@dp.message_handler(IsDeliveryCourierMessage(), regexp="confirm_delivery_order_\d+", state='*')
async def confirm_delivery_by_id(message: types.Message, state: FSMContext):
    """Подтверждаем доставку"""
    await reset_state(state, message)
    try:
        order_id = int(message.text.split('_')[-1])
        if order_id in await db.get_accepted_delivery_orders_ids_for_courier(message.from_user.id):
            order_data = await db.get_delivery_order_data(order_id)
            await message.answer(f'Заказ № {order_data["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order_data["delivery_order_id"])}'
                                 f'Сумма заказа: {order_data["delivery_order_final_price"]} руб.\n'
                                 f'Адрес доставки: {order_data["location_name"]}\n'
                                 f'{order_data["location_address"]}\n'
                                 f'Время создания {order_data["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order_data["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order_data["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order_data["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order_data["delivery_order_status"]}\n',
                                 reply_markup=await gen_confirm_order_markup(order_data["delivery_order_id"]))
        else:
            await message.answer(f'Нет принятого и не доставленного заказа с номером № {order_id}')
    except Exception as err:
        logging.info(err)
        await message.answer('Неизвестная команда')


@dp.message_handler(IsDeliveryCourierMessage(), commands=['unaccepted_delivery_orders'], state='*')
async def get_unaccepted_delivery_orders(message: types.Message, state: FSMContext):
    """Список заказов, ожидающих подтверждения"""
    await reset_state(state, message)
    orders = await db.get_unaccepted_delivery_orders_for_courier(message.from_user.id)
    if orders:
        await message.answer('Список заказов, ожидающих подтверждения:')
        for order in orders:
            await message.answer(f'{blue_diamond_em} Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n',
                                 reply_markup=await gen_courier_confirm_markup(order["delivery_order_id"],
                                                                               order["delivery_order_courier_id"]))
    else:
        await message.answer('Нет заказов, ожидающих подтверждения.')
