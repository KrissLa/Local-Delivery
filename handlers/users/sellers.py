from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone

from filters.users_filters import IsSellerCallback, IsSellerMessage
from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import confirm_order_seller_data, couriers_data, active_order_data, \
    order_is_delivered, confirm_bonus_order, active_bonus_order_data, bonus_order_is_delivered_data
from keyboards.inline.inline_keyboards import generate_couriers_keyboard, generate_active_order_keyboard, \
    generate_active_bonus_order_keyboard
from loader import dp, db, bot
from states.sellers_states import SelectCourier
from utils.send_messages import send_message_to_courier_order, \
    send_confirm_message_to_user_pickup, send_confirm_message_to_user_delivery


@dp.message_handler(IsSellerMessage(), commands=['im_at_work'], state=['*'])
async def im_at_work(message: types.Message):
    """Ставим статус на работе"""
    await db.im_at_work_seller(message.from_user.id, 'true')
    await message.answer('Теперь Вы будете получать заказы')


@dp.message_handler(IsSellerMessage(), commands=['im_at_home'], state=['*'])
async def im_at_home(message: types.Message):
    """Ставим статус дома"""
    await db.im_at_work_seller(message.from_user.id, 'false')
    await message.answer('Теперь Вы не будете получать заказы')


@dp.callback_query_handler(confirm_order_seller_data.filter(status='confirm'), state=['*'])
async def seller_confirms_order(call: CallbackQuery, callback_data: dict):
    """Продавец нажимает принять ордер"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    order_taked = await db.take_order(order_id)
    if order_taked:
        time_user_location = await db.get_time_and_user_id(order_id)
        print(time_user_location)
        delivery_to = datetime.now(timezone('Europe/Moscow')) + timedelta(minutes=time_user_location[0])
        print(delivery_to.strftime("%H:%M"))
        await db.update_deliver_to(order_id, delivery_to)
        delivery_method = callback_data.get('delivery_method')
        if delivery_method == 'Заберу сам':
            await send_confirm_message_to_user_pickup(time_user_location[1], order_id, delivery_to.strftime("%H:%M"))
            await call.message.answer(f'Заказ № {order_id} подтвержден!\n'
                                      f'Нужно приготовить к {delivery_to.strftime("%H:%M")}\n'
                                      f'Не забудьте отметить готовность заказа. Найти его можно в /active_orders')
        else:
            couriers = await db.get_couriers_for_location(time_user_location[2])
            if couriers:
                await call.message.answer('Выберите курьера:',
                                          reply_markup=await generate_couriers_keyboard(couriers, order_id))
                await SelectCourier.WaitCourier.set()
            else:
                await call.message.answer('Нет доступных курьеров. Свяжитесь с кем-нибудь. Заказ потом можно найти в '
                                          '/unaccepted_orders')
    else:
        await call.message.answer('Заказ уже обработан. Посмотреть заказы можно в /active_orders')


@dp.callback_query_handler(couriers_data.filter(), state=SelectCourier.WaitCourier)
async def select_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Продавец выбирает курьера"""
    await call.message.edit_reply_markup()
    courier_tg_id = int(callback_data.get("courier_tg_id"))
    courier_name = await db.get_courier_name(courier_tg_id)
    order_id = int(callback_data.get('order_id'))
    await db.update_order_courier(order_id, courier_name, courier_tg_id)
    order_info = await db.get_order_info_for_courier(order_id)
    await send_message_to_courier_order(courier_tg_id, order_info)
    await send_confirm_message_to_user_delivery(order_info, courier_name)
    await call.message.answer("Уведомления курьеру и клиенту отправлены."
                              'Не забудьте отметить готовность заказа. Посмотреть заказы можно в /active_orders')
    await state.finish()


@dp.callback_query_handler(confirm_order_seller_data.filter(status='cancel'), state=['*'])
async def seller_cancel_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Продавец нажимает отклонить ордер"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data['order_id'])
    await state.update_data(order_reason_id=order_id)
    if await db.get_order_status(order_id) == "Ожидание подтверждения продавца":
        await db.update_order_status(order_id, 'Отклонен')
        await call.message.answer("Укажите причину отклонения заказа")
        await SelectCourier.WaitReason.set()
    else:
        await call.message.answer("Заказ уже обработан. Посмотреть заказы можно в /active_orders")


@dp.message_handler(state=SelectCourier.WaitReason)
async def get_reason(message: types.Message, state: FSMContext):
    """Причина отклонения заказа"""
    reason = message.text
    data = await state.get_data()
    order_id = data.get('order_reason_id')
    user_id = await db.get_user_tg_id(order_id)
    await db.update_reason_for_rejection(order_id, reason)
    await bot.send_message(user_id, f'Ваш заказ № {order_id} отклонен.\n'
                                    f'Причина: {reason}')
    await message.answer("Заказ отклонен. Пользователь получил уведомление.")
    await state.finish()


@dp.message_handler(IsSellerMessage(), commands=['active_orders'], state=["*"])
async def get_active_orders(message: types.Message):
    """Показать список всех принятых заказов"""
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_active_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            if order['delivery_method'] == 'С доставкой':
                await message.answer(text=f'Заказ № {order["order_id"]}\n'
                                          f'{order["order_info"]}\n'
                                          f'C доставкой\n'
                                          f'Доставить к {order["deliver_to"].strftime("%H:%M")}',
                                     reply_markup=await generate_active_order_keyboard(order))
            else:
                await message.answer(text=f'Заказ № {order["order_id"]}\n'
                                          f'{order["order_info"]}\n'
                                          'Самовывоз\n'
                                          f'Приготовить к {order["deliver_to"].strftime("%H:%M")}',
                                     reply_markup=await generate_active_order_keyboard(order))
    else:
        await message.answer('Нет принятых заказов')


@dp.callback_query_handler(active_order_data.filter(delivery_method='С доставкой'))
async def order_ready(call: CallbackQuery, callback_data: dict):
    """Отмечаем заказ готов"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    if await db.ready_order(order_id):
        order_detail = await db.get_ready_order_for_courier(order_id)
        await bot.send_message(chat_id=order_detail['order_courier_telegram_id'],
                               text=f"Заказ № {order_id} готов для доставки!\n"
                                    f"{order_detail['order_info']}\n"
                                    f"Адрес достаки: {order_detail['order_local_object_name']}, \n"
                                    f"{order_detail['delivery_address']}\n"
                                    f"Стоимость заказа: {order_detail['order_price']}\n"
                                    f"Доставить нужно к {order_detail['deliver_to'].strftime('%H:%M')}\n"
                                    f"Не забудьте подтвердить заказ после доставки."
                                    f"Посмотреть все готовые для доставки заказы и подтвердить их: /all_ready_orders")
        await bot.send_message(client_id,
                               f'Ваш заказ № {order_id} готов. Курьер уже в пути.')
        await call.message.answer("Уведомление курьеру и клиенту отправлено")
    else:
        await call.message.answer("Заказ уже обработан.")


@dp.callback_query_handler(active_order_data.filter(delivery_method='Заберу сам'))
async def order_ready(call: CallbackQuery, callback_data: dict):
    """Отмечаем заказ готов"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    if await db.ready_order(order_id):
        order_detail = await db.get_ready_order_for_courier(order_id)
        await bot.send_message(chat_id=user_id,
                               text=f"Ваш заказ № {order_id} готов!\n"
                                    f"{order_detail['order_info']}\n"
                                    f"Пожалуйста, заберите заказ по адресу:\n"
                                    f"{order_detail['delivery_address']}\n"
                                    f"Стоимость заказа: {order_detail['order_price']}\n")
        await call.message.answer("Уведомление клиенту отправлено, не забудьте подтвердить "
                                  "выдачу товара /confirm_delivery")
    else:
        await call.message.answer("Заказ уже обработан.")


# Список заказов, ожидающих принятия
@dp.message_handler(IsSellerMessage(), commands=['unaccepted_orders'], state=["*"])
async def get_active_orders(message: types.Message):
    """Показать список всех непринятых заказов"""
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_unaccepted_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            if order['delivery_method'] == "С доставкой":
                mes = f"""Новый заказ № {order['order_id']}
            {order['order_info']}
            Тип доставки: {order['delivery_method']}
            Адрес доставки: {order["order_local_object_name"]},
            {order["delivery_address"]}
            Доставить через {order["time_for_delivery"]} минут
            Пропуск для курьеров: {order["order_pass_for_courier"]}
            Цена заказа: {order["order_price"]} руб.
            Статус заказа: {order["order_status"]}"""
            else:
                mes = f"""
            Новый заказ № {order['order_id']}
            {order['order_info']}
            Тип доставки: {order['delivery_method']}
            {order["delivery_address"]}
            Приготовить через {order["time_for_delivery"]} минут
            Цена заказа: {order["order_price"]} руб.
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
                                                     delivery_method=order['delivery_method'])
                                             )
                                         ],
                                         [
                                             InlineKeyboardButton(
                                                 text=f'Отклонить заказ № {order["order_id"]}',
                                                 callback_data=confirm_order_seller_data.new(
                                                     order_id=order["order_id"],
                                                     status='cancel',
                                                     delivery_method=order['delivery_method'])
                                             )
                                         ]

                                     ]
                                 )
                                 )
    else:
        await message.answer("Нет непринятых заказов")


# список заказов, с кнопкой подтверждения о выдаче заказа на кассе

@dp.message_handler(IsSellerMessage(), commands=['confirm_delivery'], state=['*'])
async def confirm_delivery_seller(message: types.Message):
    """Подтверждение выдачи товара продавцом"""
    location_id = await db.get_seller_location_id(message.from_user.id)
    sellers_confirm_orders = await db.get_all_ready_orders_for_sellers(location_id)
    if sellers_confirm_orders:
        for order in sellers_confirm_orders:
            await message.answer(f'Заказ № {order["order_id"]}.\n'
                                 f'{order["order_info"]}'
                                 f'Приготовить в {order["deliver_to"].strftime("%H:%M")}\n'
                                 f'Статус заказ: {order["order_status"]}\n'
                                 f'Стоимость заказа: {order["order_price"]} руб',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Заказ выдан!',
                                             callback_data=order_is_delivered.new(order_id=order["order_id"],
                                                                                  user_id=order[
                                                                                      'order_user_telegram_id'])
                                         )
                                     ]
                                 ]))
    else:
        await message.answer('Пока нет готовых к выдаче заказов.')


@dp.callback_query_handler(IsSellerCallback(), order_is_delivered.filter())
async def confirm_delivery_courier(call: CallbackQuery, callback_data: dict):
    """Продавец подтверждает выдачу"""
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    if await db.order_is_delivered(order_id, user_id):
        await call.message.answer(f'Заказ № {order_id} выдан!')
        await bot.send_message(user_id,
                               f'Ваш заказ № {order_id} выдан.\n'
                               f'Приятного аппетита!')
    else:
        await call.message.answer('Заказ уже отмечен как выдан.')


@dp.callback_query_handler(confirm_bonus_order.filter(), state=['*'])
async def confirm_bonus_order_seller(call: CallbackQuery, callback_data: dict):
    """Подтверждение бонусного заказа"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('b_order_id'))
    bonus_status = await db.get_bonus_order_status(b_order_id)
    if bonus_status == 'Отклонен':
        await call.message.answer('Заказ отменен пользователем')
    elif bonus_status == 'Подтвержден, готовится':
        await call.message.answer('Заказ уже принят другим продавцом')
    elif bonus_status == 'Ожидание продавца':
        await db.set_bonus_order_status(order_id=b_order_id,
                                        status='Подтвержден, готовится')
        bonus_order_info = await db.get_bonus_order_info_by_id(b_order_id)
        await bot.send_message(chat_id=bonus_order_info['bonus_order_user_telegram_id'],
                               text=f"Ваш бонусный заказ № {bonus_order_info['bonus_order_id']}Б подтвержден.\n"
                                    f"Когда он будет готов Вам придет уведомление.\n"
                                    f"Чтобы вернуться к функциям бота, пожалуйста, нажмите кнопку.",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [
                                       InlineKeyboardButton(
                                           text='Отлично!',
                                           callback_data='return_to_bot'
                                       )
                                   ]
                               ]))
        await call.message.answer(f'Бонусный заказ № {bonus_order_info["bonus_order_id"]}Б подтвержден\n'
                                  f'Когда он будет готов, сообщите клиенту: /confirm_readiness_bonus_orders')
    else:
        await call.message.answer('Заказ уже обработан')


@dp.message_handler(IsSellerMessage(), commands=['confirm_readiness_bonus_orders'], state=['*'])
async def set_ready_bonus_orders(message: types.Message):
    """Получаем список ативных бонусных заказов"""
    location_id = await db.get_seller_location_id(message.from_user.id)
    order_list = await db.get_active_bonus_orders_by_location_id(location_id)
    if order_list:
        for order in order_list:
            await message.answer(text=f'Заказ № {order["bonus_order_id"]}Б\n'
                                      f'Количество бонусных роллов - {order["bonus_quantity"]} шт.\n',
                                 reply_markup=await generate_active_bonus_order_keyboard(order))
    else:
        await message.answer('Пока нет бонусных заказов')


@dp.callback_query_handler(active_bonus_order_data.filter(), state=['*'])
async def confirm_readiness_bonus(call: CallbackQuery, callback_data: dict):
    """Отмечааем бонусный заказ как готов"""
    b_order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    await db.set_bonus_order_status(b_order_id, 'Готов')
    await bot.send_message(client_id,
                           f"Ваш бонусный заказ № {b_order_id}Б готов!\n"
                           f"Подойдите к продавцу чтобы забрать его.")
    await call.message.answer(
        "Уведомление клиенту отправлено! После выдачи заказа отметьте его в /confirm_bonus_orders")


@dp.message_handler(IsSellerMessage(), commands=['confirm_bonus_orders'], state=['*'])
async def bonus_orders_to_confirm_delivery(message: types.Message):
    """Список бонусных заказов к выдаче"""
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


@dp.callback_query_handler(bonus_order_is_delivered_data.filter(), state=['*'])
async def bonus_order_is_delivered(call: CallbackQuery, callback_data: dict):
    """Отмечаем бонусынй заказ как выдан"""
    b_order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    await db.set_bonus_order_status(b_order_id, 'Выдан')
    bonus_order_info = await db.get_bonus_order_info_by_id(b_order_id)
    await bot.send_message(client_id,
                           f'Ваш заказ № {bonus_order_info["bonus_order_id"]}Б - {bonus_order_info["bonus_quantity"]} '
                           f'выдан.\n'
                           f'Приятного аппетита!',
                           reply_markup=menu_keyboard)
    await call.message.answer(f'Готово. Заказ № {bonus_order_info["bonus_order_id"]}Б выдан.')
