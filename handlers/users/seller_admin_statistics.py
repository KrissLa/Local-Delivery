import logging
import os
from datetime import datetime, timedelta

import xlsxwriter
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import statistics_date_data, statistics_year_data, statistics_year_month_data, \
    statistics_day_data
from keyboards.inline.statistics_keyboards import gen_years_keyboard, period_markup, gen_months_keyboard, months_names, \
    gen_days_keyboard
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.emoji import warning_em
from utils.statistics import get_order_statistics, get_indicators, get_bonus_order_statistics, get_seller_statistics, \
    get_courier_statistics, get_client_statistics


@dp.callback_query_handler(text='cancel_statistics')
async def cancel_statistics(call: CallbackQuery, state: FSMContext):
    """Отмена"""
    await call.message.edit_reply_markup()
    await call.message.answer('Вы отменили операцию')
    await state.finish()


@dp.callback_query_handler(statistics_date_data.filter(period='all_time'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    # logging.info()
    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за все время на {datetime.now(timezone("Europe/Moscow")).strftime("%d.%m.%Y")}.xlsx'
    workbook = xlsxwriter.Workbook(path)
    orders = await db.get_orders_by_location(location['location_id'])
    bonus_orders = await  db.get_bonus_orders_by_location(location['location_id'])

    first_period = await db.get_first_order_date(location['location_id'])
    end_period = await db.get_last_order_date(location['location_id'])

    indicators = await db.get_indicators_by_location(location['location_id'])
    bonus_indicators = await db.get_bonus_indicators(location['location_id'])

    sellers = await db.get_seller_ids_by_location(location['location_id'])
    couriers = await db.get_courier_ids_by_location(location['location_id'])
    clients = await db.get_clients_ids_by_location(location['location_id'])

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_period.strftime("%d.%m.%Y"), end_period.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_period.strftime("%d.%m.%Y"),
                                     end_period.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_period.strftime("%d.%m.%Y"), end_period.strftime("%d.%m.%Y"))
    await get_courier_statistics(workbook, couriers, first_period.strftime("%d.%m.%Y"), end_period.strftime("%d.%m.%Y"))
    await get_client_statistics(workbook, clients, location['location_id'], first_period.strftime("%d.%m.%Y"),
                                end_period.strftime("%d.%m.%Y"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='today'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)
    today = datetime.now(timezone("Europe/Moscow"))

    # logging.info()
    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за {today.strftime("%d.%m.%Y")}.xlsx'
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    bonus_orders = await  db.get_bonus_orders_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date(location['location_id'],
                                                                      today.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"),
                                today.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"),
                                 today.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], today.strftime("%d.%m.%Y"),
                                today.strftime("%d.%m.%Y"), today.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='yesterday'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)
    day = datetime.now(timezone("Europe/Moscow")) - timedelta(days=1)

    # logging.info()
    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за {day.strftime("%d.%m.%Y")}.xlsx'
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))
    bonus_orders = await  db.get_bonus_orders_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date(location['location_id'],
                                                                      day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date(location['location_id'], day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, day.strftime("%d.%m.%Y"), day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, day.strftime("%d.%m.%Y"), day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, day.strftime("%d.%m.%Y"), day.strftime("%d.%m.%Y"),
                                day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, day.strftime("%d.%m.%Y"), day.strftime("%d.%m.%Y"),
                                 day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], day.strftime("%d.%m.%Y"),
                                day.strftime("%d.%m.%Y"), day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='this_week'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

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

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {day_list[0].strftime("%d.%m.%Y")}-{day_list[-1].strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], day_list[0].strftime("%Y-%m-%d"),
                                                             day_list[-1].strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         day_list[0].strftime("%Y-%m-%d"),
                                                                         day_list[-1].strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     day_list[0].strftime("%Y-%m-%d"),
                                                                     day_list[-1].strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             day_list[0].strftime("%Y-%m-%d"),
                                                                             day_list[-1].strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  day_list[0].strftime("%Y-%m-%d"),
                                                                  day_list[-1].strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    day_list[0].strftime("%Y-%m-%d"),
                                                                    day_list[-1].strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   day_list[0].strftime("%Y-%m-%d"),
                                                                   day_list[-1].strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, day_list[0].strftime("%d.%m.%Y"), day_list[-1].strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, day_list[0].strftime("%d.%m.%Y"),
                                     day_list[-1].strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, day_list[0].strftime("%d.%m.%Y"), day_list[-1].strftime("%d.%m.%Y"),
                                first_date=day_list[0].strftime("%Y-%m-%d"),
                                last_date=day_list[-1].strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, day_list[0].strftime("%d.%m.%Y"),
                                 day_list[-1].strftime("%d.%m.%Y"),
                                 first_date=day_list[0].strftime("%Y-%m-%d"),
                                 last_date=day_list[-1].strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], day_list[0].strftime("%d.%m.%Y"),
                                day_list[-1].strftime("%d.%m.%Y"), first_date=day_list[0].strftime("%Y-%m-%d"),
                                last_date=day_list[-1].strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='last_week'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    if day.weekday() == 0:
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)
    else:
        while day.weekday() != 0:
            day -= timedelta(days=1)
        last_day = day - timedelta(days=1)
        first_day = last_day - timedelta(days=6)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='this_month'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='last_month'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")), 1) - timedelta(days=1)
    first_day = datetime(int(day.strftime("%Y")), int(day.strftime("%m")) - 1, 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='this_year'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    last_day = day
    first_day = datetime(int(day.strftime("%Y")), 1, 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='last_year'))
async def get_statistics(call: CallbackQuery):
    """Получаем статистику за все время"""
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(int(day.strftime("%Y")) - 1, 12, 31)
    first_day = datetime(int(day.strftime("%Y")) - 1, 1, 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за период {first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")}.xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='by_years'))
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Статистика по годам"""
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await SellerAdmin.Year.set()


@dp.callback_query_handler(text='back_to_statistics', state=[SellerAdmin.Year,
                                                             SellerAdmin.Month,
                                                             SellerAdmin.Day])
async def back_from_year(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите период врмени, за который хотите получить статистику.',
                              reply_markup=period_markup)
    await state.finish()


@dp.callback_query_handler(statistics_year_data.filter(), state=SellerAdmin.Year)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по году"""
    year = int(callback_data["year"])
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    day = datetime.now(timezone("Europe/Moscow"))
    last_day = datetime(year, 12, 31)
    first_day = datetime(year, 1, 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за {year} год .xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=SellerAdmin.Month)
@dp.callback_query_handler(statistics_date_data.filter(period='by_months'))
async def get_statistics(call: CallbackQuery):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await SellerAdmin.Month.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=SellerAdmin.Month)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц, за который хотите получить статистику.",
                              reply_markup=await gen_months_keyboard(year, months))


@dp.callback_query_handler(statistics_year_month_data.filter(), state=SellerAdmin.Month)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Показываем статистику за месяц и год"""
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    first_day = datetime(year, month, 1)

    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за {months_names[month]} {year} года .xlsx '
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date_period(location['location_id'], first_day.strftime("%Y-%m-%d"),
                                                             last_day.strftime("%Y-%m-%d"))
    bonus_orders = await db.get_bonus_orders_by_location_and_date_period(location['location_id'],
                                                                         first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date_period(location['location_id'],
                                                                     first_day.strftime("%Y-%m-%d"),
                                                                     last_day.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date_period(location['location_id'],
                                                                             first_day.strftime("%Y-%m-%d"),
                                                                             last_day.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date_period(location['location_id'],
                                                                  first_day.strftime("%Y-%m-%d"),
                                                                  last_day.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date_period(location['location_id'],
                                                                    first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date_period(location['location_id'],
                                                                   first_day.strftime("%Y-%m-%d"),
                                                                   last_day.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, first_day.strftime("%d.%m.%Y"),
                                     last_day.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, first_day.strftime("%d.%m.%Y"), last_day.strftime("%d.%m.%Y"),
                                first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, first_day.strftime("%d.%m.%Y"),
                                 last_day.strftime("%d.%m.%Y"),
                                 first_date=first_day.strftime("%Y-%m-%d"),
                                 last_date=last_day.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], first_day.strftime("%d.%m.%Y"),
                                last_day.strftime("%d.%m.%Y"), first_date=first_day.strftime("%Y-%m-%d"),
                                last_date=last_day.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)


@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=SellerAdmin.Day)
@dp.callback_query_handler(statistics_date_data.filter(period='by_days'))
async def get_statistics(call: CallbackQuery):
    """Статистика по дням"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await SellerAdmin.Day.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=SellerAdmin.Day)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц",
                              reply_markup=await gen_months_keyboard(year, months))

@dp.callback_query_handler(statistics_year_month_data.filter(), state=SellerAdmin.Day)
async def get_month(call: CallbackQuery, callback_data: dict):
    """Получаем месяц"""
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    days = await db.get_orders_days(year, month)
    await call.message.answer("Выберите день, за который хотите получить статистику.",
                              reply_markup=await gen_days_keyboard(days, year))


@dp.callback_query_handler(statistics_day_data.filter(), state=SellerAdmin.Day)
async def get_statistics_by_day(call: CallbackQuery, callback_data: dict):
    """Статистика за день"""
    day = int(callback_data["day"])
    month = int(callback_data["month"])
    year = int(callback_data["year"])
    await call.message.answer("Собираю статистику\n"
                              f"{warning_em} Пожалуйста, подождите. Это может занять несколько минут")
    location = await db.get_seller_admin_location_id(call.from_user.id)
    try:
        os.makedirs(f"statistics/location_{location['location_id']}")
    except Exception as err:
        logging.error(err)
    today = datetime(year, month, day)

    # logging.info()
    path = f'statistics/location_{location["location_id"]}/Статистика {location["location_name"]} за {today.strftime("%d.%m.%Y")}.xlsx'
    workbook = xlsxwriter.Workbook(path)

    orders = await db.get_orders_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    bonus_orders = await  db.get_bonus_orders_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    indicators = await db.get_indicators_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    bonus_indicators = await db.get_bonus_indicators_by_location_date(location['location_id'],
                                                                      today.strftime("%Y-%m-%d"))

    sellers = await db.get_seller_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    couriers = await db.get_courier_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))
    clients = await db.get_clients_ids_by_location_and_date(location['location_id'], today.strftime("%Y-%m-%d"))

    await get_indicators(workbook, indicators, bonus_indicators)
    await get_order_statistics(workbook, orders, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"))
    await get_bonus_order_statistics(workbook, bonus_orders, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"))
    await get_seller_statistics(workbook, sellers, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"),
                                today.strftime("%Y-%m-%d"))
    await get_courier_statistics(workbook, couriers, today.strftime("%d.%m.%Y"), today.strftime("%d.%m.%Y"),
                                 today.strftime("%Y-%m-%d"))
    await get_client_statistics(workbook, clients, location['location_id'], today.strftime("%d.%m.%Y"),
                                today.strftime("%d.%m.%Y"), today.strftime("%Y-%m-%d"))

    workbook.close()
    report = open(path, 'rb')
    await bot.send_document(call.from_user.id, report)
    report.close()
    os.remove(path)



