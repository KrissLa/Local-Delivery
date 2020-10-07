from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import IsSellerMessage
from keyboards.inline.callback_datas import confirm_order_seller_data, order_is_delivered, \
    bonus_order_is_delivered_data, active_order_cancel_data
from keyboards.inline.inline_keyboards import generate_active_order_keyboard, generate_active_bonus_order_keyboard
from loader import dp, db
from utils.check_states import states_for_menu, reset_state
from utils.emoji import success_em, error_em
from utils.product_list import get_product_list


@dp.message_handler(IsSellerMessage(), commands=['im_at_work'], state=states_for_menu)
@dp.message_handler(IsSellerMessage(), commands=['im_at_work'], state=['*'])
async def im_at_work(message: types.Message, state: FSMContext):
    """Ставим статус на работе"""
    await reset_state(state, message)
    await db.im_at_work_seller(message.from_user.id, 'true')
    await message.answer(f'{success_em} Теперь Вы будете получать заказы')


@dp.message_handler(IsSellerMessage(), commands=['im_at_home'], state=states_for_menu)
@dp.message_handler(IsSellerMessage(), commands=['im_at_home'], state=['*'])
async def im_at_home(message: types.Message, state: FSMContext):
    """Ставим статус дома"""
    await reset_state(state, message)
    await db.im_at_work_seller(message.from_user.id, 'false')
    await message.answer(f'{error_em} Теперь Вы не будете получать заказы')


@dp.message_handler(IsSellerMessage(), commands=['active_orders'], state=["*"])
async def get_active_orders(message: types.Message, state: FSMContext):
    """Показать список всех принятых заказов"""
    await reset_state(state, message)
    order_list = await db.get_active_orders_by_seller(message.from_user.id)
    if order_list:
        for order in order_list:

            if order['order_delivery_method'] == 'Доставка':
                courier_name = await db.get_courier_name_by_id(order['order_courier_id'])
                await message.answer(text=f'Заказ № {order["order_id"]}\n'
                                          f'{await get_product_list(order["order_id"])}\n'
                                          f'Стоимомть заказа: {order["order_final_price"]} руб.\n'
                                          f'C доставкой\n'
                                          f'Курьер: {courier_name}\n'
                                          f'Доставить к {order["order_time_for_delivery"].strftime("%H:%M")}',
                                     reply_markup=await generate_active_order_keyboard(order))
            else:
                await message.answer(text=f'Заказ № {order["order_id"]}\n'
                                          f'{await get_product_list(order["order_id"])}\n'
                                          f'Стоимомть заказа: {order["order_final_price"]} руб.\n'
                                          'Самовывоз\n'
                                          f'Приготовить к {order["order_time_for_delivery"].strftime("%H:%M")}',
                                     reply_markup=await generate_active_order_keyboard(order))
    else:
        await message.answer('Нет принятых заказов')


# Список заказов, ожидающих принятия
@dp.message_handler(IsSellerMessage(), commands=['unaccepted_orders'], state=["*"])
async def get_active_orders(message: types.Message, state: FSMContext):
    """Показать список всех непринятых заказов"""
    await reset_state(state, message)
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_unaccepted_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            if order['order_delivery_method'] == "Доставка":
                mes = f"""Новый заказ № {order['order_id']}
{await get_product_list(order["order_id"])}
Тип доставки: {order['order_delivery_method']}
Адрес доставки: {order["local_object_name"]},
{order["order_address"]}
Дата заказа {order['order_date'].strftime("%d.%m.%Y")}
Время заказа: {order['order_created_at'].strftime("%H:%M")}
Доставить через {order["order_deliver_through"]} минут
Пропуск для курьеров: {order["order_pass_to_courier"]}
Цена заказа: {order["order_final_price"]} руб.
Статус заказа: {order["order_status"]}"""
            else:
                mes = f"""
Новый заказ № {order['order_id']}
{await get_product_list(order["order_id"])}
Тип доставки: {order['order_delivery_method']}
{order["order_address"]}
Дата заказа {order['order_date'].strftime("%d.%m.%Y")}
Время заказа: {order['order_created_at'].strftime("%H:%M")}
Приготовить через {order["order_deliver_through"]} минут
Цена заказа: {order["order_final_price"]} руб.
Статус заказа: {order["order_status"]}"""
            await message.answer(mes,
                                 reply_markup=InlineKeyboardMarkup(
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(
                                                 text=f'Принять заказ № {order["order_id"]}',
                                                 callback_data=confirm_order_seller_data.new(
                                                     order_id=order["order_id"],
                                                     status='confirm',
                                                     delivery_method=order['order_delivery_method'])
                                             )
                                         ],
                                         [
                                             InlineKeyboardButton(
                                                 text=f'Отклонить заказ № {order["order_id"]}',
                                                 callback_data=confirm_order_seller_data.new(
                                                     order_id=order["order_id"],
                                                     status='cancel',
                                                     delivery_method=order['order_delivery_method'])
                                             )
                                         ]

                                     ]
                                 )
                                 )
    else:
        await message.answer("Нет непринятых заказов")

###########88888888888
# список заказов, с кнопкой подтверждения о выдаче заказа на кассе

@dp.message_handler(IsSellerMessage(), commands=['confirm_delivery'], state=['*'])
async def confirm_delivery_seller(message: types.Message, state: FSMContext):
    """Подтверждение выдачи товара продавцом"""
    await reset_state(state, message)
    sellers_confirm_orders = await db.get_delivery_orders_by_seller(message.from_user.id)
    if sellers_confirm_orders:
        for order in sellers_confirm_orders:
            await message.answer(f'Заказ № {order["order_id"]}.\n'
                                 f'{await get_product_list(order["order_id"])}\n'
                                 f'Приготовить в {order["order_time_for_delivery"].strftime("%H:%M")}\n'
                                 f'Статус заказ: {order["order_status"]}\n'
                                 f'Стоимость заказа: {order["order_final_price"]} руб',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text=f'Заказ {order["order_id"]} выдан!',
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
        await message.answer('Пока нет готовых к выдаче заказов.')


@dp.message_handler(IsSellerMessage(), commands=['confirm_readiness_bonus_orders'], state=['*'])
async def set_ready_bonus_orders(message: types.Message, state: FSMContext):
    """Получаем список ативных бонусных заказов"""
    await reset_state(state, message)
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_active_bonus_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            await message.answer(text=f'Заказ № {order["bonus_order_id"]}Б\n'
                                      f'Количество бонусных роллов - {order["bonus_quantity"]} шт.\n',
                                 reply_markup=await generate_active_bonus_order_keyboard(order))
    else:
        await message.answer('Пока нет бонусных заказов')


@dp.message_handler(IsSellerMessage(), commands=['confirm_bonus_orders'], state=['*'])
async def bonus_orders_to_confirm_delivery(message: types.Message, state: FSMContext):
    """Список бонусных заказов к выдаче"""
    await reset_state(state, message)
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_ready_bonus_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            await message.answer(f'Бонусный заказ № {order["bonus_order_id"]}Б.\n'
                                 f'Количество бонусных роллов - {order["bonus_quantity"]} шт.',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Заказ выдан!',
                                             callback_data=bonus_order_is_delivered_data.new(
                                                 order_id=order["bonus_order_id"],
                                                 user_id=order[
                                                     'bonus_order_user_telegram_id'])
                                         )
                                     ]
                                 ]))
    else:
        await message.answer('Пока нет готовых к выдаче бонусных заказов.')