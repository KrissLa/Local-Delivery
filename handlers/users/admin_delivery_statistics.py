import logging
import os
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import statistics_location_data_del, statistics_date_delivery
from keyboards.inline.statistics_keyboards import delivery_period_markup
from loader import dp, db
from utils.emoji import warning_em


@dp.callback_query_handler(statistics_location_data_del.filter(location_id='all_locations'))
async def show_statistics_keyboard(call: CallbackQuery, state: FSMContext):
    """Показываем клавиатуру с выбором периода статистики"""
    await call.message.edit_reply_markup()
    await call.message.answer('Теперь выберите период',
                              reply_markup=delivery_period_markup)
    await state.finish()



@dp.callback_query_handler(statistics_date_delivery.filter(period='all_time'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за все время на {datetime.now(timezone("Europe/Moscow")).strftime("%d.%m.%Y")}'
    first_period = await db.get_first_delivery_order_date_admin()
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_period,
        'end_period': datetime.now(timezone("Europe/Moscow")),

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_orders(),
        'products': list(await db.get_order_products_admin()),
        'numbers': await db.get_orders_count_admin(),

        'indicators': await db.get_indicators(),
        'bonus_indicators': await db.get_bonus_indicators_admin(),
        'indicators_by_loc': await db.get_admin_indicators_by_loc(),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc(),

        'bonus_orders': await db.get_bonus_orders(),

        'sellers_orders': await db.get_sellers_orders_admin(),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin(),

        'couriers_orders': await db.get_couriers_orders_admin(),

        'user_orders': await db.get_users_orders_admin(),
        'user_bonus_orders': await db.get_users_bonus_orders_admin(),

    }

    await send_admin_statistics(data)