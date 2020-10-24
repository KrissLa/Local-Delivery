import asyncio
import logging
import os
from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import statistics_date_data, statistics_year_data, statistics_year_month_data, \
    statistics_day_data
from keyboards.inline.statistics_keyboards import gen_years_keyboard, period_markup, gen_months_keyboard, months_names, \
    gen_days_keyboard
from loader import dp, db, bot
from states.admin_state import AddAdmin
from states.seller_admin_states import SellerAdmin
from utils.emoji import warning_em, success_em, error_em
from utils.statistics import write_statistics


async def run_blocking_tasks(data):
    """"""

    loop = asyncio.get_running_loop()

    mail_was_send = await loop.run_in_executor(
        None, write_statistics, data)
    if mail_was_send:
        await bot.send_message(data['user_id'], f"{success_em} Статистика отправлена Вам на почту {data['to_email']}.")
    else:
        await bot.send_message(data['user_id'], f"{error_em} Не удалось отправить статистику по адресу {data['to_email']}."
                                                f" Проверьте e-mail адрес и попробуйте еще раз.")


@dp.callback_query_handler(text='cancel_statistics', state='*')
async def cancel_statistics(call: CallbackQuery, state: FSMContext):
    """Отмена"""
    await call.message.edit_reply_markup()
    await call.message.answer('Вы отменили операцию')
    await state.finish()


@dp.callback_query_handler(statistics_date_data.filter(period='all_time'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за все время"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за все время на {datetime.now(timezone("Europe/Moscow")).strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)
    first_day = await db.get_first_order_date(location['location_id'])
    if first_day:
        first_period = first_day
    else:
        first_period = datetime.now(timezone("Europe/Moscow"))

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': first_period,
        'end_period': datetime.now(timezone("Europe/Moscow")),

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_orders_by_location(location['location_id']),
        'products': list(await db.get_order_products_by_location(location['location_id'])),
        'numbers': await db.get_orders_count(location['location_id']),

        'indicators': await db.get_indicators_by_location(location['location_id']),
        'bonus_indicators': await db.get_bonus_indicators(location['location_id']),

        'bonus_orders': await db.get_bonus_orders_by_location(location['location_id']),

        'sellers_orders': await db.get_sellers_orders(location['location_id']),
        'sellers_bonus': await db.get_sellers_bonus_orders(location['location_id']),

        'couriers_orders': await db.get_couriers_orders(location['location_id']),

        'user_orders': await db.get_users_orders(location['location_id']),
        'user_bonus_orders': await db.get_users_bonus_orders(location['location_id']),

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='today'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за сегодня"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    today = datetime.now(timezone("Europe/Moscow"))
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} {today.strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': today,
        'end_period': today,

        'path_to_dir': path_to_dir,
        'file_name': file_name,
        'path': f'{path_to_dir}/{file_name}.xlsx',

        'orders': await db.get_orders_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"),
                                                           today.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"),
                                                             today.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"),
                                                                  today.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"),
                                                                   today.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          today.strftime("%Y-%m-%d"),
                                                                          today.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       today.strftime("%Y-%m-%d"),
                                                                       today.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      today.strftime("%Y-%m-%d"),
                                                                      today.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           today.strftime("%Y-%m-%d"),
                                                                           today.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        today.strftime("%Y-%m-%d"),
                                                                        today.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 today.strftime("%Y-%m-%d"),
                                                                 today.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             today.strftime("%Y-%m-%d"),
                                                                             today.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='yesterday'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за вчера"""
    day = datetime.now(timezone("Europe/Moscow")) - timedelta(days=1)
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} {day.strftime("%d.%m.%Y")}'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"),
                                                           day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"),
                                                             day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"),
                                                                  day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"),
                                                                   day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          day.strftime("%Y-%m-%d"),
                                                                          day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       day.strftime("%Y-%m-%d"),
                                                                       day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      day.strftime("%Y-%m-%d"),
                                                                      day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           day.strftime("%Y-%m-%d"),
                                                                           day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        day.strftime("%Y-%m-%d"),
                                                                        day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 day.strftime("%Y-%m-%d"),
                                                                 day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             day.strftime("%Y-%m-%d"),
                                                                             day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='this_week'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за текущую неделю"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
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
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за текущую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='last_week'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за прошедшую неделю"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = datetime.now(timezone("Europe/Moscow"))
    if day.weekday() == 0:
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    else:
        while day.weekday() != 0:
            day -= timedelta(days=1)
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за прошедшую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='this_month'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за текущий месяц"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за текущий месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='last_month'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за прошедший месяц"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1) - timedelta(days=1)
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")) - 1, 1)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за прошедший месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='this_year'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за текущий год"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), 1, 1)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за текущий год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='last_year'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Получаем статистику за прошедший год"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:Statistics':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")) - 1, 12, 31)
    first_day = datetime(int(day.strftime("%Y")) - 1, 1, 1)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за прошедший год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='by_years'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))

    if await state.get_state() == 'AddAdmin:Statistics':
        await AddAdmin.LocYear.set()
    else:
        await SellerAdmin.Year.set()


@dp.callback_query_handler(text='back_to_statistics', state=[SellerAdmin.Year,
                                                             SellerAdmin.Month,
                                                             SellerAdmin.Day,
                                                             AddAdmin.LocYear,
                                                             AddAdmin.LocMonth,
                                                             AddAdmin.LocDay])
async def back_from_year(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите период врмени, за который хотите получить статистику.',
                              reply_markup=period_markup)
    if await state.get_state() in ['AddAdmin:LocYear', 'AddAdmin:LocMonth', 'AddAdmin:LocDay']:
        await AddAdmin.Statistics.set()
    else:
        await state.finish()


@dp.callback_query_handler(statistics_year_data.filter(), state=[SellerAdmin.Year, AddAdmin.LocYear])
async def get_year(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем статистику по году"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:LocYear':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    year = int(callback_data["year"])

    last_day = datetime(year, 12, 31)
    first_day = datetime(year, 1, 1)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за {year} год'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=SellerAdmin.Month)
@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    if await state.get_state() == 'AddAdmin:Statistics':
        await AddAdmin.LocMonth.set()
    else:
        await SellerAdmin.Month.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=[SellerAdmin.Month, AddAdmin.LocMonth])
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц, за который хотите получить статистику.",
                              reply_markup=await gen_months_keyboard(year, months))


@dp.callback_query_handler(statistics_year_month_data.filter(), state=[SellerAdmin.Month, AddAdmin.LocMonth])
async def get_year(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Показываем статистику за месяц и год"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:LocMonth':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    year = int(callback_data["year"])
    month = int(callback_data["month"])

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    first_day = datetime(year, month, 1)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за {months_names[month]} {year} года'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)


@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=[SellerAdmin.Day, AddAdmin.LocDay])
@dp.callback_query_handler(statistics_date_data.filter(period='by_days'), state='*')
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Статистика по дням"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    if await state.get_state() in  ['AddAdmin:Statistics', 'AddAdmin:LocDay']:
        await AddAdmin.LocDay.set()
    else:
        await SellerAdmin.Day.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=[SellerAdmin.Day, AddAdmin.LocDay])
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц",
                              reply_markup=await gen_months_keyboard(year, months))


@dp.callback_query_handler(statistics_year_month_data.filter(), state=[SellerAdmin.Day, AddAdmin.LocDay])
async def get_month(call: CallbackQuery, callback_data: dict):
    """Получаем месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    days = await db.get_orders_days(year, month)
    await call.message.answer("Выберите день, за который хотите получить статистику.",
                              reply_markup=await gen_days_keyboard(days, year))


@dp.callback_query_handler(statistics_day_data.filter(), state=[SellerAdmin.Day, AddAdmin.LocDay])
async def get_statistics_by_day(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Статистика за день"""
    await call.message.edit_reply_markup()
    if await state.get_state() == 'AddAdmin:LocDay':
        email = await db.get_email_admin(call.from_user.id)
        loc = await state.get_data()
        location = await db.get_admin_location_id(loc['location_id'])
    else:
        email = await db.get_email_seller(call.from_user.id)
        location = await db.get_seller_admin_location_id(call.from_user.id)
    day = int(callback_data["day"])
    month = int(callback_data["month"])
    year = int(callback_data["year"])

    last_day = datetime(year, month, day)
    first_day = datetime(year, month, day)

    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/location_{location["location_id"]}'
    file_name = f'Статистика {location["location_name"]} за {last_day.strftime("%d.%m.%Y")}'

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

        'orders': await db.get_orders_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_by_location_and_date(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_by_location_and_date(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_location_and_date(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_by_loc_and_date(location['location_id'],
                                                                          first_day.strftime("%Y-%m-%d"),
                                                                          last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_location_and_date(location['location_id'],
                                                                       first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_by_loc_and_date(location['location_id'],
                                                                      first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_by_loc_and_date(location['location_id'],
                                                                           first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_by_loc_and_date(location['location_id'],
                                                                        first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_by_loc_and_date(location['location_id'],
                                                                 first_day.strftime("%Y-%m-%d"),
                                                                 last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_by_loc_and_date(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    }

    await run_blocking_tasks(data)





@dp.callback_query_handler(text='cancek_delivery_stat', state='*')
async def back(call: CallbackQuery, state: FSMContext):
    """back"""
    await call.message.edit_reply_markup()
    await call.message.answer('Вы отменили операцию')
    await state.finish()
