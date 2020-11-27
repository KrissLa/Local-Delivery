import logging
import os
from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import statistics_location_data_del, statistics_date_delivery, \
    statistics_delivery_year_data, statistics_delivery_year_month_data, statistics_delivery_day_data, \
    statistics_date_location_delivery, statistics_year_location_data, statistics_delivery_year_month_loc_data, \
    statistics_delivery_day_loc_data
from keyboards.inline.statistics_keyboards import delivery_period_markup, gen_delivery_years_keyboard, \
    generate_locations_keyboard_del, gen_delivery_months_keyboard, months_names, gen_days_keyboard, \
    gen_delivery_days_keyboard, generate_delivery_period_keyboard, gen_delivery_loc_years_keyboard, gen_months_keyboard, \
    gen_delivery_days_keyboard_loc
from loader import dp, db
from states.admin_state import AddAdmin
from utils.emoji import warning_em
from utils.statistics import send_admin_delivery_statistics


@dp.callback_query_handler(text='back_to_statistics_seller', state='*')
async def back(call: CallbackQuery, state: FSMContext):
    """back"""
    location_id = await db.get_seller_admin_location(call.from_user.id)
    await call.message.answer('Выберите локацию, по которой хотите получить статистику',
                              reply_markup=await generate_delivery_period_keyboard(location_id, admin=False))
    await state.finish()


@dp.callback_query_handler(text='back_to_loc')
async def back(call: CallbackQuery):
    """Назад"""
    await call.message.edit_reply_markup()
    locations = await db.get_all_delivery_locations()
    await call.message.answer('Выберите локацию, по которой хотите получить статистику',
                              reply_markup=await generate_locations_keyboard_del(locations))


@dp.callback_query_handler(text='back_to_del_stat', state=[AddAdmin.DeliveryMonth, AddAdmin.DeliveryDay])
@dp.callback_query_handler(text='back_to_del_stat')
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
    first_day = await db.get_first_delivery_order_date_admin()
    if first_day:
        first_period = first_day
    else:
        first_period = datetime.now(timezone("Europe/Moscow"))
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

        'orders': await db.get_delivery_orders_stat(),
        'products': list(await db.get_delivery_order_products_admin()),
        'numbers': await db.get_delivery_orders_count_admin(),

        'indicators': await db.get_delivery_indicators(),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc(),

        'sellers_orders': await db.get_sellers_delivery_orders_admin(),

        'couriers_orders': await db.get_couriers_delivery_orders_admin(),

        'user_orders': await db.get_users_delivery_orders_admin()

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='today'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    first_day = day
    last_day = day
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за {day.strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': day,
        'end_period': day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='yesterday'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow")) - timedelta(days=1)
    first_day = day
    last_day = day
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за {day.strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': day,
        'end_period': day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='this_week'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    day_list = []
    if day.weekday() == 6:
        day_list.append(day)
        day -= timedelta(days=1)
        while day.weekday() != 6:
            day_list.append(day)
            day -= timedelta(days=1)
    else:
        while day.weekday() != 6:
            day_list.append(day)
            day -= timedelta(days=1)
    day_list.reverse()
    first_day = day_list[0]
    last_day = day_list[-1]
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за текущую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='last_week'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    if day.weekday() == 0:
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    else:
        while day.weekday() != 0:
            day -= timedelta(days=1)
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за прошедшую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='this_month'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за текущий месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='last_month'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1) - timedelta(days=1)
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")) - 1, 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за прошедший месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='this_year'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), 1, 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за текущий год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='last_year'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")) - 1, 12, 31)
    first_day = datetime(int(day.strftime("%Y")) - 1, 1, 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за прошедший год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='by_years'))
async def get_all_statistics(call: CallbackQuery):
    """Собираем статистику"""
    await call.message.edit_reply_markup()
    years = await db.get_delivery_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_delivery_years_keyboard(years))


@dp.callback_query_handler(statistics_delivery_year_data.filter())
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])

    last_day = datetime(year, 12, 31)
    first_day = datetime(year, 1, 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за {year} год'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='by_months'), state=AddAdmin.DeliveryMonth)
@dp.callback_query_handler(statistics_date_delivery.filter(period='by_months'))
async def get_all_statistics(call: CallbackQuery):
    """Собираем статистику"""
    await call.message.edit_reply_markup()
    years = await db.get_delivery_orders_years()
    await call.message.answer('Сначала выберите год',
                              reply_markup=await gen_delivery_years_keyboard(years))
    await AddAdmin.DeliveryMonth.set()


@dp.callback_query_handler(statistics_delivery_year_data.filter(), state=AddAdmin.DeliveryMonth)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_delivery_orders_months(year)
    await call.message.answer('Выберите месяц',
                              reply_markup=await gen_delivery_months_keyboard(year, months))


@dp.callback_query_handler(statistics_delivery_year_month_data.filter(), state=AddAdmin.DeliveryMonth)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    month = int(callback_data["month"])

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    first_day = datetime(year, month, 1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за {months_names[month]} {year} года'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_delivery.filter(period='by_months'), state=AddAdmin.DeliveryDay)
@dp.callback_query_handler(statistics_date_delivery.filter(period='by_days'))
async def get_all_statistics(call: CallbackQuery):
    """Собираем статистику"""
    await call.message.edit_reply_markup()
    years = await db.get_delivery_orders_years()
    await call.message.answer('Сначала выберите год',
                              reply_markup=await gen_delivery_years_keyboard(years))
    await AddAdmin.DeliveryDay.set()


@dp.callback_query_handler(statistics_delivery_year_data.filter(), state=AddAdmin.DeliveryDay)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_delivery_orders_months(year)
    await call.message.answer('Теперь выберите месяц',
                              reply_markup=await gen_delivery_months_keyboard(year, months))


@dp.callback_query_handler(statistics_delivery_year_month_data.filter(), state=AddAdmin.DeliveryDay)
async def get_month(call: CallbackQuery, callback_data: dict):
    """Получаем месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    days = await db.get_delivery_orders_days(year, month)
    await call.message.answer("Выберите день, за который хотите получить статистику.",
                              reply_markup=await gen_delivery_days_keyboard(days, month, year))


@dp.callback_query_handler(statistics_delivery_day_data.filter(), state=AddAdmin.DeliveryDay)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику"""
    await call.message.edit_reply_markup()
    day = int(callback_data["day"])
    month = int(callback_data["month"])
    year = int(callback_data["year"])

    last_day = datetime(year, month, day)
    first_day = datetime(year, month, day)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/all'
    file_name = f'Статистика оптовых заказов по всем точкам продаж за {last_day.strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_date(first_day.strftime("%Y-%m-%d"),
                                                            last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_by_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                               last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_location_data_del.filter(), state=[AddAdmin.DeliveryLocMonth,
                                                                         AddAdmin.DeliveryLocDay])
@dp.callback_query_handler(statistics_location_data_del.filter())
async def show_statistics_keyboard(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Показываем клавиатуру с выбором периода статистики"""
    print('poimal')
    await call.message.edit_reply_markup()
    location_id = int(callback_data['location_id'])
    await call.message.answer('Теперь выберите период',
                              reply_markup=await generate_delivery_period_keyboard(location_id))
    await state.finish()


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='all_time'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за все время на {datetime.now(timezone("Europe/Moscow")).strftime("%d.%m.%Y")}'
    first_day = await db.get_first_delivery_order_date_admin_by_loc(location["location_id"])
    if first_day:
        first_period = first_day
    else:
        first_period = datetime.now(timezone("Europe/Moscow"))
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

        'orders': await db.get_delivery_orders_stat_by_loc(location["location_id"]),
        'products': list(await db.get_delivery_order_products_admin_by_loc(location["location_id"])),
        'numbers': await db.get_delivery_orders_count_admin_by_loc(location["location_id"]),

        'indicators': await db.get_delivery_indicators_by_loc(location["location_id"]),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc(location["location_id"]),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc(location["location_id"]),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc(location["location_id"]),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc(location["location_id"])

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='today'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    today = datetime.now(timezone("Europe/Moscow"))
    first_day = today
    last_day = today
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} {today.strftime("%d.%m.%Y")}'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='yesterday'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    today = datetime.now(timezone("Europe/Moscow")) - timedelta(days=1)
    first_day = today
    last_day = today
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} {today.strftime("%d.%m.%Y")}'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='this_week'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    day_list = []
    if day.weekday() == 6:
        day_list.append(day)
        day -= timedelta(days=1)
        while day.weekday() != 6:
            day_list.append(day)
            day -= timedelta(days=1)
    else:
        while day.weekday() != 6:
            day_list.append(day)
            day -= timedelta(days=1)
    day_list.reverse()
    first_day = day_list[0]
    last_day = day_list[-1]
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за текущую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='last_week'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    if day.weekday() == 0:
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    else:
        while day.weekday() != 0:
            day -= timedelta(days=1)
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за прошедшую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='this_month'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за текущий месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='last_month'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1) - timedelta(days=1)
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")) - 1, 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за прошедший месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='this_year'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), 1, 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за текущий год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='last_year'))
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")) - 1, 12, 31)
    first_day = datetime(int(day.strftime("%Y")) - 1, 1, 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за прошедший год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='by_years'))
async def get_statistics(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    admin_status = callback_data['admin']
    if admin_status == 'True':
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        location = await db.get_seller_admin_location_id(call.from_user.id)
    years = await db.get_delivery_orders_years_by_loc(location["location_id"])
    await call.message.answer('Выберите год',
                              reply_markup=await gen_delivery_loc_years_keyboard(years, location['location_id'],
                                                                                 admin_status))


@dp.callback_query_handler(statistics_year_location_data.filter())
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    year = int(callback_data["year"])
    last_day = datetime(year, 12, 31)
    first_day = datetime(year, 1, 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов {location["location_name"]} за {year} год'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='this_month'),
                           state=AddAdmin.DeliveryLocMonth)
@dp.callback_query_handler(statistics_date_location_delivery.filter(period='by_months'))
async def get_statistics(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    admin_status = callback_data['admin']
    if admin_status == 'True':
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        location = await db.get_seller_admin_location_id(call.from_user.id)
    years = await db.get_delivery_orders_years_by_loc(location["location_id"])
    await call.message.answer('Сначала выберите год',
                              reply_markup=await gen_delivery_loc_years_keyboard(years, location['location_id'],
                                                                                 admin_status))

    await AddAdmin.DeliveryLocMonth.set()


@dp.callback_query_handler(statistics_year_location_data.filter(), state=AddAdmin.DeliveryLocMonth)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    location_id = int(callback_data['location_id'])
    admin_status = callback_data['admin']
    months = await db.get_delivery_orders_months_by_loc(year, location_id)
    await call.message.answer("Выберите месяц, за который хотите получить статистику.",
                              reply_markup=await gen_delivery_months_keyboard(year, months, location_id, admin_status))


@dp.callback_query_handler(statistics_delivery_year_month_loc_data.filter(), state=AddAdmin.DeliveryLocMonth)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    year = int(callback_data["year"])
    month = int(callback_data["month"])

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    first_day = datetime(year, month, 1)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов за {months_names[month]} {year} года'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)


@dp.callback_query_handler(statistics_date_location_delivery.filter(period='this_month'), state=AddAdmin.DeliveryLocDay)
@dp.callback_query_handler(statistics_date_location_delivery.filter(period='by_days'))
async def get_statistics(call: CallbackQuery, callback_data: dict):
    """Статистика по дням"""
    await call.message.edit_reply_markup()
    admin_status = callback_data['admin']
    if admin_status == 'True':
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        location = await db.get_seller_admin_location_id(call.from_user.id)
    years = await db.get_delivery_orders_years_by_loc(location['location_id'])
    await call.message.answer('Сначала выберите год',
                              reply_markup=await gen_delivery_loc_years_keyboard(years, location['location_id'],
                                                                                 admin_status))
    await AddAdmin.DeliveryLocDay.set()


@dp.callback_query_handler(statistics_year_location_data.filter(), state=AddAdmin.DeliveryLocDay)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    location_id = int(callback_data['location_id'])
    admin_status = callback_data['admin']
    months = await db.get_delivery_orders_months_by_loc(year, location_id)
    await call.message.answer("Теперь выберите месяц",
                              reply_markup=await gen_delivery_months_keyboard(year, months, location_id, admin_status))


@dp.callback_query_handler(statistics_delivery_year_month_loc_data.filter(), state=AddAdmin.DeliveryLocDay)
async def get_month(call: CallbackQuery, callback_data: dict):
    """Получаем месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    location_id = int(callback_data['location_id'])
    admin = callback_data['admin']
    days = await db.get_delivery_orders_days_by_loc(year, month, location_id)
    await call.message.answer("Выберите день, за который хотите получить статистику.",
                              reply_markup=await gen_delivery_days_keyboard_loc(days, month, year, location_id, admin))


@dp.callback_query_handler(statistics_delivery_day_loc_data.filter(), state=AddAdmin.DeliveryLocDay)
async def get_all_statistics(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по всем локациям"""
    day = int(callback_data["day"])
    month = int(callback_data["month"])
    year = int(callback_data["year"])

    last_day = datetime(year, month, day)
    first_day = datetime(year, month, day)
    admin_status = callback_data['admin']
    if admin_status == 'True':
        email = await db.get_email_admin(call.from_user.id)
        location = await db.get_admin_location_id(int(callback_data['location_id']))
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/delivery/location_{location["location_id"]}'
    file_name = f'Статистика оптовых заказов за {last_day.strftime("%d.%m.%Y")} года'
    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_day,
        'end_period': last_day,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_delivery_orders_stat_by_loc_date(location["location_id"], first_day.strftime("%Y-%m-%d"),
                                                                last_day.strftime("%Y-%m-%d")),
        'products': list(await db.get_delivery_order_products_admin_by_loc_date(location["location_id"],
                                                                                first_day.strftime("%Y-%m-%d"),
                                                                                last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_delivery_orders_count_admin_by_loc_date(location["location_id"],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_delivery_indicators_by_loc_date(location["location_id"],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_delivery_indicators_by_loc_loc_date(location["location_id"],
                                                                                    first_day.strftime("%Y-%m-%d"),
                                                                                    last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                 first_day.strftime("%Y-%m-%d"),
                                                                                 last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                                   first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_delivery_orders_admin_by_loc_date(location["location_id"],
                                                                            first_day.strftime("%Y-%m-%d"),
                                                                            last_day.strftime("%Y-%m-%d"))

    }

    await send_admin_delivery_statistics(data)
