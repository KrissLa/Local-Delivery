import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_datas import courier_confirm_data, confirm_delivery_order
from loader import dp, db, bot
from utils.emoji import success_em, error_em, warning_em


@dp.callback_query_handler(courier_confirm_data.filter(status='confirm'))
async def get_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Курьер принимает заказ"""
    await call.message.edit_reply_markup()
    await db.update_delivery_order_status(int(callback_data["order_id"]),
                                          'Заказ подтвержден')
    await call.message.answer(f"{success_em}, Готово.\n"
                              f"Заказ № {int(callback_data['order_id'])} принят.\n"
                              f"{warning_em} Подтвердить доставку /confirm_delivery_order")
    admin = await db.get_delivery_admin_tg_id(int(callback_data["order_id"]))
    await bot.send_message(admin, f"{success_em} Курьер принял заказ № {int(callback_data['order_id'])}")


@dp.callback_query_handler(courier_confirm_data.filter(status='cancel'))
async def get_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Курьер не принимает заказ"""
    await call.message.edit_reply_markup()
    await db.update_delivery_order_courier_and_status_cancel(int(callback_data["order_id"]))
    await call.message.answer(f"{success_em}, Готово.\n"
                              f"Заказ № {int(callback_data['order_id'])} отклонен.")
    admin = await db.get_delivery_admin_tg_id(int(callback_data["order_id"]))
    courier_name = await db.get_delivery_courier_name(call.from_user.id)
    await bot.send_message(admin,
                           f"{error_em} Курьер {courier_name} не принял заказ № {int(callback_data['order_id'])}\n"
                           f"{warning_em} Заказ перенесен в /delivery_order_set_courier\n"
                           f"Нажмите /delivery_order_set_courier_{int(callback_data['order_id'])} чтобы выбрать другого курьера")



###########
@dp.callback_query_handler(confirm_delivery_order.filter())
async def confirm_delivery_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Подтверждаем доставку заказа"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await db.update_delivery_order_delivered_at(order_id, 'Заказ выполнен')
    order_owner = await db.get_delivery_order_owner(order_id)
    admin_id = await db.get_delivery_admin_telg_id(order_id)
    try:
        await bot.send_message(admin_id, f'{success_em} Заказ на поставку продуктов № {order_id} доставлен.')
    except Exception as err:
        logging.error(err)
    try:
        await bot.send_message(order_owner, f'{success_em} Ваш заказ на поставку продуктов № {order_id} доставлен.')
        await call.message.answer(f'{success_em} Заказ № {order_id} доставлен.\n')
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{success_em} Заказ № {order_id} доставлен.\n'
                                  f'{error_em} Не удалось отправить уведомление о доставке админу локации.')
    await state.finish()
