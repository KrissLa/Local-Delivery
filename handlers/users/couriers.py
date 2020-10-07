import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from filters.users_filters import IsCourierCallback
from keyboards.inline.callback_datas import order_is_delivered, active_order_cancel_data, reviev_order_data
from keyboards.inline.inline_keyboards import back_markup
from loader import dp, db, bot
from states.sellers_states import SelectCourier
from utils.emoji import success_em, error_em, attention_em, warning_em


@dp.callback_query_handler(IsCourierCallback(), order_is_delivered.filter())
async def confirm_delivery_courier(call: CallbackQuery, callback_data: dict):
    """Курьер подтверждает доставку"""
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    if await db.order_is_not_canceled(order_id):
        await db.update_order_status(order_id, "Выполнен")
        await db.update_order_delivered_at(order_id)
        await db.order_is_delivered(user_id)
        try:
            await bot.send_message(user_id,
                                   f'{success_em} Ваш заказ № {order_id} доставлен.\n'
                                   f'Приятного аппетита!',
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [
                                           InlineKeyboardButton(
                                               text='Написать отзыв',
                                               callback_data=reviev_order_data.new(order_id=order_id)
                                           )
                                       ]
                                   ])
                                   )
            await call.message.answer(f'{success_em} Заказ № {order_id} доставлен!')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f'{error_em}Не удалось отправить уведомление пользователю.\n'
                                      f'{success_em}Заказ отмечен как доставлен.')
    else:
        await call.message.answer(f"{error_em} Заказ отменен.")


@dp.callback_query_handler(IsCourierCallback(), text='back', state=SelectCourier.WaitReasonCourier)
async def cancel_order_back(call: CallbackQuery, state: FSMContext):
    """Отменяем отмену заказа"""
    await call.message.edit_reply_markup()
    await call.answer('Готово')
    await call.message.answer(f"{attention_em} Заказы готовые к доставке /all_ready_orders")
    await state.finish()


@dp.callback_query_handler(active_order_cancel_data.filter())
async def cancel_active_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отмена заказа продавцом"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data['order_id'])
    await state.update_data(order_reason_id=order_id)
    await call.message.answer(f"{warning_em} Укажите причину отклонения заказа",
                              reply_markup=back_markup)
    await SelectCourier.WaitReasonCourier.set()


@dp.message_handler(state=SelectCourier.WaitReasonCourier)
async def get_reason(message: types.Message, state: FSMContext):
    """Причина отклонения заказа"""
    reason = message.text
    data = await state.get_data()
    order_id = data.get('order_reason_id')
    user_id = await db.get_user_tg_id(order_id)
    admin_id = await db.get_seller_admin_tg_id(order_id)
    await db.update_reason_for_rejection_courier(order_id, reason)
    try:
        await bot.send_message(user_id, f'{error_em}Ваш заказ № {order_id} отклонен.\n'
                                        f'Причина: {reason}')
        try:
            await bot.send_message(admin_id, f'{error_em} Заказ № {order_id} отклонен курьером.\n'
                                             f'Причина: {reason}')
            await message.answer(f"{success_em} Заказ отклонен. Пользователь получил уведомление.")
        except Exception as err:
            logging.error(err)
            await message.answer(f"{success_em} Заказ отклонен. Пользователь получил уведомление.")

    except Exception as err:
        logging.error(err)
        await message.answer(f"{success_em} Заказ отклонен. \n"
                             f"{error_em} Не удалось отправить уведомление клиенту.")

    await state.finish()

