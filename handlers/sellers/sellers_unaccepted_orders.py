import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import confirm_order_seller_data, couriers_data
from keyboards.inline.inline_keyboards import generate_couriers_keyboard, back_markup
from loader import dp, db, bot
from states.sellers_states import SelectCourier
from utils.emoji import success_em, attention_em, warning_em, error_em
from utils.send_messages import send_confirm_message_to_user_pickup, send_message_to_courier_order, \
    send_confirm_message_to_user_delivery


@dp.callback_query_handler(confirm_order_seller_data.filter(status='confirm'), state=['*'])
async def seller_confirms_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Продавец нажимает принять ордер"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    order_taked = await db.take_order(order_id, call.from_user.id)
    await state.update_data(order_id=order_id)
    if order_taked:
        time_user_location = await db.get_time_and_user_id(order_id)
        accepted = datetime.now(timezone('Europe/Moscow'))
        delivery_to = accepted + timedelta(minutes=time_user_location['order_deliver_through'])
        await db.update_deliver_to(order_id, delivery_to, accepted)
        delivery_method = callback_data.get('delivery_method')
        if delivery_method == 'Самовывоз':
            await db.update_order_status(order_id, "Принят")
            try:
                await send_confirm_message_to_user_pickup(time_user_location["user_telegram_id"], order_id,
                                                          delivery_to.strftime("%H:%M"))
                await call.message.answer(f'{success_em} Заказ № {order_id} подтвержден!\n'
                                          f'Нужно приготовить к {delivery_to.strftime("%H:%M")}\n'
                                          f'{warning_em} Не забудьте подтвердить что заказ готов. \n'
                                          f'{attention_em} Посмотреть заказы можно в /active_orders')
            except Exception as err:
                logging.error(err)
                await call.message.answer(f'{error_em}Не удалось отправить уведомление пользователю.\n'
                                          f'{success_em}Заказ № {order_id} подтвержден!\n'
                                          f'Нужно приготовить к {delivery_to.strftime("%H:%M")}\n'
                                          f'{warning_em} Не забудьте подтвердить что заказ готов. \n'
                                          f'{attention_em} Посмотреть заказы можно в /active_orders')
        else:
            couriers = await db.get_couriers_for_location(time_user_location["location_id"])
            if couriers:
                await call.message.answer('Выберите курьера:',
                                          reply_markup=await generate_couriers_keyboard(couriers, order_id))
                await SelectCourier.WaitCourier.set()
            else:
                await db.reset_order_time_and_seller(order_id)
                await call.message.answer(f'{error_em} Нет доступных курьеров. Свяжитесь с кем-нибудь. \n'
                                          f'Потом принять заказ можно в /unaccepted_orders')
    else:
        await call.message.answer(f'{error_em}Заказ уже обработан.')


@dp.callback_query_handler(couriers_data.filter(), state=SelectCourier.WaitCourier)
async def select_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Продавец выбирает курьера"""
    await call.message.edit_reply_markup()
    courier_tg_id = int(callback_data.get("courier_tg_id"))
    courier_name = await db.get_courier_name(courier_tg_id)
    order_id = int(callback_data.get('order_id'))
    await db.update_order_courier(order_id, courier_tg_id)
    order_info = await db.get_order_data(order_id)
    if await send_message_to_courier_order(order_id, courier_tg_id, order_info):
        await db.update_order_status(order_id, "Принят")
        try:
            await send_confirm_message_to_user_delivery(order_id, order_info, courier_name)
            await call.message.answer(f'{success_em} Уведомления курьеру и клиенту отправлены. \n'
                                      f'{warning_em} Не забудьте подтвердить что заказ '
                                      'готов для доставки. \n'
                                      f'{attention_em} Посмотреть заказы можно в /active_orders\n')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f"{error_em} Не удалось отправить уведомление пользователю\n"
                                      f"{success_em} Уведомление курьеру отправлено.\n"
                                      f'{warning_em} Не забудьте подтвердить что заказ готов для доставки. \n'
                                      f'{attention_em} Посмотреть заказы можно в /active_orders')
    else:
        await db.reset_order_time_and_seller(order_id)
        await call.message.answer(f'{error_em} Не удалось отправить сообщение курьеру. Свяжитесь с кем-нибудь. \n'
                                  f'{warning_em} Потом принять заказ можно в /unaccepted_orders')

    await state.finish()


@dp.callback_query_handler(text='back', state=SelectCourier.WaitReason)
async def cancel_order_back(call: CallbackQuery, state: FSMContext):
    """Отменяем отмену заказа"""
    await call.message.edit_reply_markup()
    await call.message.answer(f"{attention_em} Заказ перенесен в непринятые.\n"
                              f"Непринятые заказы - /unaccepted_orders\n"
                              f"Принятые - /active_orders")
    await state.finish()


@dp.callback_query_handler(confirm_order_seller_data.filter(status='cancel'), state=['*'])
async def seller_cancel_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Продавец нажимает отклонить ордер"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data['order_id'])
    await state.update_data(order_reason_id=order_id)
    await call.message.answer(f"{warning_em} Укажите причину отклонения заказа",
                              reply_markup=back_markup)
    await SelectCourier.WaitReason.set()


@dp.message_handler(state=SelectCourier.WaitReason)
async def get_reason(message: types.Message, state: FSMContext):
    """Причина отклонения заказа"""

    reason = message.text
    data = await state.get_data()
    order_id = data.get('order_reason_id')
    user_id = await db.get_user_tg_id(order_id)
    if await db.take_order(order_id, message.from_user.id):
        admin_id = await db.get_seller_admin_tg_id(order_id)
        await db.update_reason_for_rejection(order_id, reason)
        await bot.send_message(user_id, f'{error_em}Ваш заказ № {order_id} отклонен.\n'
                                        f'Причина: {reason}')
        await bot.send_message(admin_id, f'{error_em} Заказ № {order_id} отклонен продавцом.\n'
                                        f'Причина: {reason}')

        await message.answer(f"{success_em} Заказ отклонен. Пользователь получил уведомление.")
    else:
        await message.answer(f'{error_em} Заказ уже обработан')
    await state.finish()


