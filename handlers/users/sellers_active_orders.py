import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsSellerCallback
from keyboards.inline.callback_datas import active_order_data, active_order_cancel_data
from keyboards.inline.inline_keyboards import back_markup
from loader import dp, db, bot
from states.sellers_states import SelectCourier
from utils.emoji import warning_em, attention_em, success_em, attention_em_red, error_em
from utils.product_list import get_product_list


@dp.callback_query_handler(active_order_data.filter(delivery_method='Доставка'))
async def order_ready(call: CallbackQuery, callback_data: dict):
    """Отмечаем заказ готов"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('user_id'))

    order_detail = await db.get_active_order_data(order_id)
    # order_detail = await db.get_ready_order_for_courier(order_id)
    try:
        await bot.send_message(chat_id=order_detail['courier_telegram_id'],
                               text=f"{attention_em_red} Заказ № {order_id} готов для доставки!\n"
                                    f"{await get_product_list(order_id)}\n"
                                    f"Адрес доставки: {order_detail['local_object_name']}, \n"
                                    f"{order_detail['order_address']}\n"
                                    f"Стоимость заказа: {order_detail['order_final_price']} руб.\n"
                                    f"Доставить нужно к {order_detail['order_time_for_delivery'].strftime('%H:%M')}\n"
                                    f"{warning_em} Не забудьте подтвердить заказ после доставки.\n"
                                    f"{attention_em} Посмотреть все готовые для доставки заказы и подтвердить их: "
                                    f"/all_ready_orders")
        try:
            await bot.send_message(client_id,
                                   f'{success_em} Ваш заказ № {order_id} готов. Курьер уже в пути.')
            await db.update_order_status(order_id, "Приготовлен")
            await call.message.answer(f"{success_em}Уведомление курьеру и клиенту отправлено")
        except Exception as err:
            logging.error(err)
            await db.update_order_status(order_id, "Приготовлен")
            await call.message.answer(f"{error_em} Не удалось отправить уведомление клиенту.\n"
                                      f"{success_em} Уведомление курьеру отправлено!")
    except Exception as err:
        logging.error(err)
        await db.update_order_status(order_id, "Приготовлен")
        await call.message.answer(f"{error_em} Не удалось отправить уведомление курьеру  и пользователю.\n"
                                  f"{success_em} Заказ отмечен как готов.")


@dp.callback_query_handler(active_order_data.filter(delivery_method='Самовывоз'))
async def order_ready(call: CallbackQuery, callback_data: dict):
    """Отмечаем заказ готов"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    user_id = int(callback_data.get('user_id'))
    order_detail = await db.get_active_order_little_data(order_id)
    await db.update_order_status(order_id, "Приготовлен")
    try:
        await bot.send_message(chat_id=user_id,
                               text=f"{success_em} Ваш заказ № {order_id} готов!\n"
                                    f"{await get_product_list(order_id)}\n"
                                    f"Пожалуйста, заберите заказ по адресу:\n"
                                    f"{order_detail['order_address']}\n"
                                    f"Стоимость заказа: {order_detail['order_final_price']} руб.\n")
        await call.message.answer(f"{success_em} Уведомление клиенту отправлено. \n"
                                  f"{warning_em} Не забудьте подтвердить выдачу товара /confirm_delivery")
    except Exception as err:
        logging.error(err)
        await call.message.answer(f"{error_em} Не получилось отправить уведомление клиенту.\n"
                                  f"{warning_em} Не забудьте подтвердить выдачу товара /confirm_delivery")


@dp.callback_query_handler(IsSellerCallback(), text='back', state=SelectCourier.WaitReasonActive)
async def cancel_order_back(call: CallbackQuery, state: FSMContext):
    """Отменяем отмену заказа"""
    await call.message.edit_reply_markup()
    await call.message.answer(f"{attention_em} Заказ находится в принятых.\n"
                              f"Непринятые заказы - /unaccepted_orders\n"
                              f"Принятые - /active_orders")
    await state.finish()


@dp.callback_query_handler(active_order_cancel_data.filter())
async def cancel_active_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отмена заказа продавцом"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data['order_id'])
    await state.update_data(order_reason_id=order_id)
    await call.message.answer(f"{warning_em} Укажите причину отклонения заказа",
                              reply_markup=back_markup)
    await SelectCourier.WaitReasonActive.set()


@dp.message_handler(state=SelectCourier.WaitReasonActive)
async def get_reason(message: types.Message, state: FSMContext):
    """Причина отклонения заказа"""
    reason = message.text
    data = await state.get_data()
    order_id = data.get('order_reason_id')
    user_id = await db.get_user_tg_id(order_id)
    admin_id = await db.get_seller_admin_tg_id(order_id)
    await db.update_reason_for_rejection(order_id, reason)
    try:
        await bot.send_message(user_id, f'{error_em}Ваш заказ № {order_id} отклонен.\n'
                                        f'Причина: {reason}')
        try:
            await bot.send_message(admin_id, f'{error_em} Заказ № {order_id} отклонен продавцом.\n'
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
