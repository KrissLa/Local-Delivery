import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_datas import take_delivery_order, dont_take_delivery_order, confirm_delivery_order, \
    cancel_courier_data, delivery_couriers_data, courier_confirm_data
from keyboards.inline.inline_keyboards import gen_take_order_markup, confirm_cancel_delivery, \
    generate_delivery_couriers_keyboard, gen_courier_confirm_markup
from loader import dp, db, bot
from states.admin_state import AddAdmin
from utils.emoji import error_em, warning_em, success_em
from utils.product_list import get_delivery_product_list
from utils.temp_orders_list import weekdays


@dp.callback_query_handler(text='back', state=AddAdmin.TakeOrdersWait)
async def back(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    order_id = data.get('order_id')
    if order_id in await db.get_unaccepted_delivery_orders_ids():
        order_data = await db.get_delivery_order_data(order_id)
        await call.message.answer(f'Заказ № {order_data["delivery_order_id"]}\n'
                                  f'{order_data["delivery_order_info"]}'
                                  f'Сумма заказа: {order_data["delivery_order_price"]} руб.\n'
                                  f'telegramID пользователя - {order_data["delivery_order_user_telegram_id"]}\n'
                                  f'Адрес доставки: {order_data["location_name"]}\n'
                                  f'{order_data["location_address"]}\n'
                                  f'Время создания {order_data["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                  f'Дата доставки: {order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                                  f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                                  f'Время доставки: {order_data["delivery_time_info"]}\n'
                                  f'Статус заказа: {order_data["delivery_order_status"]}\n',
                                  reply_markup=await gen_take_order_markup(order_data["delivery_order_id"]))
        await AddAdmin.TakeOrders.set()
    else:
        await call.message.answer(f'Нет непринятого заказ с номером № {order_id}')


@dp.callback_query_handler(cancel_courier_data.filter(), state=AddAdmin.SetCourierOrders)
async def cancel(call: CallbackQuery, state: FSMContext):
    """Отмена"""
    await call.message.edit_reply_markup()
    await call.message.answer(f"Вы отменили операцию\n"
                              f"{warning_em} Заказ можно найти в /delivery_order_set_courier")
    await state.finish()

@dp.callback_query_handler(cancel_courier_data.filter(), state=AddAdmin.TakeOrders)
async def cancel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отмена"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await db.reset_delivery_order_admin(order_id)
    await call.message.answer(f"Вы отменили принятие заказа № {order_id}\n"
                              f"{warning_em} Заказ можно найти в /take_orders")
    await state.finish()


@dp.callback_query_handler(take_delivery_order.filter(), state=AddAdmin.TakeOrders)
async def take_order_confirm(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Принять заказ"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    status = await db.get_delivery_order_status(order_id)
    delivery_info = await db.get_delivery_admin_id(order_id)
    admin_id = await db.get_admin_id(call.from_user.id)
    couriers = await db.get_delivery_couriers()
    if couriers:
        if status == 'Ожидание подтверждения' and delivery_info['delivery_order_admin_id'] is None:
            await db.update_delivery_order_admin(order_id, admin_id, 'Курьер не назначен')
            await call.message.answer(f'{success_em} Заказ № {order_id} принят.\n'
                                      f'{warning_em} Теперь выберите курьера.',
                                      reply_markup=await generate_delivery_couriers_keyboard(couriers, order_id))
        else:
            await call.message.answer(f'{error_em} Заказ уже обработан.')
            await state.finish()
    else:
        await call.message.answer(f'{error_em} Нет доступных курьеров. Вы не можете сейчас принять заказ.\n'
                                  f'Заказ можно найти в /take_orders')


@dp.callback_query_handler(delivery_couriers_data.filter(), state=[AddAdmin.TakeOrders,
                                                                   AddAdmin.SetCourierOrders])
async def get_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отправка сообщения курьеру"""
    await call.message.edit_reply_markup()
    cour_tg = int(callback_data['delivery_courier_telegram_id'])
    order = await db.get_delivery_order_data(int(callback_data['order_id']))
    cour_name = await db.get_delivery_courier_name(cour_tg)
    try:
        await bot.send_message(cour_tg,
                               f'Вам назначен новый заказ № {order["delivery_order_id"]}\n'
                               f'{await get_delivery_product_list(int(callback_data["order_id"]))}'
                               f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                               f'Адрес доставки: {order["location_name"]}\n'
                               f'{order["location_address"]}\n'
                               f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                               f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                               f'Время доставки: {order["delivery_order_time_info"]}\n',
                               reply_markup=await gen_courier_confirm_markup(int(callback_data['order_id']),
                                                                             int(callback_data['delivery_courier_id'])))
        await db.update_delivery_order_courier_and_status(int(callback_data['order_id']),
                                                          int(callback_data['delivery_courier_id']),
                                                          'Ожидание подтверждения курьером')


        await call.message.answer(f"{success_em} Уведомление курьеру {cour_name} отправлено.")
    except Exception as err:
        logging.error(err)
        await call.message.answer(f"Не удалось отправить сообщение курьеру {cour_name}")
    await state.finish()


@dp.callback_query_handler(dont_take_delivery_order.filter(), state=[AddAdmin.TakeOrders,
                                                                     AddAdmin.ConfirmDeliveryOrders])
async def take_order_cancel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отклонить заказ заказ"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await state.update_data(order_id=order_id)
    status = await db.get_delivery_order_status(order_id)
    delivery_info = await db.get_delivery_admin_id(order_id)
    if status == 'Ожидание подтверждения' and delivery_info['delivery_order_admin_id'] is None:
        await call.message.answer("Вы уверены что хотите отклонить заказ?",
                                  reply_markup=confirm_cancel_delivery)
        await AddAdmin.TakeOrdersWait.set()
    else:
        await call.message.answer(f'{error_em} Заказ уже обработан.')
        await state.finish()


@dp.callback_query_handler(text='confirm_cancel_delivery', state=AddAdmin.TakeOrdersWait)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    """Отменяем заказ"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    order_id = data.get('order_id')
    order_owner = await db.get_delivery_order_owner(order_id)
    status = await db.get_delivery_order_status(order_id)
    delivery_info = await db.get_delivery_admin_id(order_id)
    if status == 'Ожидание подтверждения' and delivery_info['delivery_order_admin_id'] is None:
        try:
            await db.update_delivery_order_status(order_id, 'Отменен поставщиком', True)
            await call.message.answer(f'{success_em} Заказ № {order_id} отменен.\n')
            await bot.send_message(order_owner, f'{error_em} Ваш заказ на поставку продуктов № {order_id} отменен.')

        except Exception as err:
            logging.error(err)
            await call.message.answer(f'{success_em} Заказ № {order_id} отменен.\n'
                                      f'{error_em} Не удалось отправить уведомление об отмене админу локации.')
    else:
        await call.message.answer(f'{error_em} Заказ уже обработан.')
        await state.finish()

    await state.finish()



