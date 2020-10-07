from aiogram.types import CallbackQuery

from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import confirm_bonus_order, active_bonus_order_data, bonus_order_is_delivered_data
from loader import dp, db, bot
from utils.emoji import warning_em, attention_em


############888888






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
                                    f"Когда он будет готов, Вам придет уведомление.\n")
        await call.message.answer(f'Бонусный заказ № {bonus_order_info["bonus_order_id"]}Б подтвержден.\n'
                                  f'{warning_em} Когда он будет готов сообщите клиенту: /confirm_readiness_bonus_orders')
    else:
        await call.message.answer('Заказ уже обработан')


@dp.callback_query_handler(active_bonus_order_data.filter(), state=['*'])
async def confirm_readiness_bonus(call: CallbackQuery, callback_data: dict):
    """Отмечааем бонусный заказ как готов"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))
    await db.set_bonus_order_status(b_order_id, 'Готов')
    await bot.send_message(client_id,
                           f"Ваш бонусный заказ № {b_order_id}Б готов!\n"
                           f"{attention_em} Подойдите к продавцу чтобы забрать его.")
    await call.message.answer(
        "Уведомление клиенту отправлено! \n"
        f"{warning_em} Не забудьте подтвердить выдачу /confirm_bonus_orders")


@dp.callback_query_handler(bonus_order_is_delivered_data.filter(), state=['*'])
async def bonus_order_is_delivered(call: CallbackQuery, callback_data: dict):
    """Отмечаем бонусынй заказ как выдан"""
    await call.message.edit_reply_markup()
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
