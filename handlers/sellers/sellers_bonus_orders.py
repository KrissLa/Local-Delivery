import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import IsSellerCallback
from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import confirm_bonus_order, active_bonus_order_data, bonus_order_is_delivered_data, \
    cancel_bonus_order_data_sellers, reviev_bonus_order_data
from keyboards.inline.inline_keyboards import back_markup
from loader import dp, db, bot
from states.sellers_states import SelectCourier
from utils.emoji import warning_em, attention_em, error_em, success_em


############888888


@dp.callback_query_handler(IsSellerCallback(), cancel_bonus_order_data_sellers.filter())
async def cancel_bonus_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отмена бонусного заказа"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('b_order_id'))
    bonus_quantity = int(callback_data.get('quantity'))
    await state.update_data(bonus_data={
        "b_order_id": b_order_id,
        "bonus_quantity": bonus_quantity
    })
    await call.message.answer(f"{warning_em} Для отклонения бонусного заказа № {b_order_id}Б укажите причину",
                              reply_markup=back_markup)
    await SelectCourier.CancelBonus.set()


@dp.message_handler(state=SelectCourier.CancelBonus)
async def get_cancel_reason(message: types.Message, state: FSMContext):
    """Получаем причину отмены заказа"""
    reason = message.text
    data = await state.get_data()
    logging.info(data)
    bonus_user_tg_id = await db.get_bonus_order_user(data["bonus_data"]["b_order_id"])
    if await db.take_bonus_order(data["bonus_data"]["b_order_id"], message.from_user.id):
        await db.set_bonus_order_status(data["bonus_data"]["b_order_id"],
                                        "Отменен продавцом",
                                        reason)
        await db.change_bonus_plus(user_id=bonus_user_tg_id,
                                   count_bonus=data["bonus_data"]["bonus_quantity"])
        await db.set_bonus_order_canceled_at(data["bonus_data"]["b_order_id"])
        await bot.send_message(bonus_user_tg_id,
                               f'{error_em}Ваш бонусный заказ № {data["bonus_data"]["b_order_id"]}Б отклонен.\n'
                               f'Причина: {reason}')

        await message.answer(f"{success_em} Заказ отклонен. Пользователь получил уведомление.")
    else:
        await message.answer(f'{error_em} Заказ уже обработан')
    await state.finish()


@dp.callback_query_handler(text='back', state=SelectCourier.CancelBonus)
async def back(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    location_id = await db.get_seller_location_id(call.from_user.id)
    order_list = await db.get_unaccepted_bonus_orders_by_location_id(location_id)
    if order_list:
        await call.message.answer("Список непринятых бонусных заказов:")
        for order in order_list:
            mes = f"""Новый бонусный заказ № {order['bonus_order_id']}Б
Количество бонусных роллов: {order['bonus_order_quantity']}
Дата заказа: {order['bonus_order_date'].strftime("%d.%m.%Y")}
Время заказа: {order['bonus_order_created_at'].strftime("%H:%M")}
Пожалуйста, подойдите к кассе и, после выбора роллов клиентом, подтвердите заказ"""
            await call.message.answer(mes,
                                      reply_markup=InlineKeyboardMarkup(
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton(
                                                      text=f'Подтвердить бонусный заказ № {order["bonus_order_id"]}Б',
                                                      callback_data=confirm_bonus_order.new(
                                                          b_order_id=order["bonus_order_id"])
                                                  )
                                              ],
                                              [
                                                  InlineKeyboardButton(
                                                      text=f'Отклонить бонусный заказ № {order["bonus_order_id"]}Б',
                                                      callback_data=cancel_bonus_order_data_sellers.new(
                                                          b_order_id=order["bonus_order_id"],
                                                          quantity=order['bonus_order_quantity']
                                                      )
                                                  )
                                              ]

                                          ]
                                      )
                                      )
    else:
        await call.message.answer("Нет непринятых бонусных заказов заказов")
    await state.finish()


@dp.callback_query_handler(confirm_bonus_order.filter(), state=['*'])
async def confirm_bonus_order_seller(call: CallbackQuery, callback_data: dict):
    """Подтверждение бонусного заказа"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('b_order_id'))
    if await db.take_bonus_order(b_order_id, call.from_user.id):
        await db.set_bonus_order_taked(order_id=b_order_id)
        await bot.send_message(chat_id=await db.get_bonus_order_user(b_order_id),
                               text=f"{success_em}Ваш бонусный заказ № {b_order_id}Б подтвержден.\n"
                                    f"Когда он будет готов, Вам придет уведомление.\n")
        await call.message.answer(f'{success_em}Бонусный заказ № {b_order_id}Б подтвержден.\n'
                                  f'{warning_em} Когда он будет готов сообщите клиенту: /active_bonus_orders')
    else:
        await call.message.answer(f'{error_em}Заказ уже обработан')


@dp.callback_query_handler(active_bonus_order_data.filter(), state=['*'])
async def confirm_readiness_bonus(call: CallbackQuery, callback_data: dict):
    """Отмечааем бонусный заказ как готов"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    await db.set_bonus_order_status(b_order_id, 'Готов')
    await bot.send_message(client_id,
                           f"{success_em}Ваш бонусный заказ № {b_order_id}Б готов!\n"
                           f"{attention_em} Подойдите к продавцу чтобы забрать его.")
    await call.message.answer(
        f"{success_em}Уведомление клиенту отправлено! \n"
        f"{warning_em} Не забудьте подтвердить выдачу /confirm_bonus_delivery")


@dp.callback_query_handler(bonus_order_is_delivered_data.filter(), state=['*'])
async def bonus_order_is_delivered(call: CallbackQuery, callback_data: dict):
    """Отмечаем бонусынй заказ как выдан"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    await db.set_bonus_order_status(b_order_id, 'Выдан')
    await db.set_bonus_order_delivered_at(b_order_id)
    await bot.send_message(client_id,
                           f'{success_em}Ваш заказ № {b_order_id}Б выдан.\n'
                           f'Приятного аппетита!',
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [
                                   InlineKeyboardButton(
                                       text='Написать отзыв',
                                       callback_data=reviev_bonus_order_data.new(order_id=b_order_id)
                                   )
                               ]
                           ]))
    await call.message.answer(f'{success_em} Готово. Заказ № {b_order_id}Б выдан.')
