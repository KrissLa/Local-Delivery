import logging
import os
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pytz import timezone

from filters.users_filters import IsAdminMessage
from keyboards.inline.callback_datas import statistics_location_data, admin_statistics_date_data_all, \
    statistics_date_data, statistics_year_data, statistics_year_month_data, statistics_day_data
from keyboards.inline.statistics_keyboards import admin_period_markup, generate_locations_keyboard, gen_years_keyboard, \
    gen_months_keyboard, months_names, gen_days_keyboard, period_markup
from loader import db, dp
from states.admin_state import AddAdmin

from utils.emoji import warning_em, success_em, error_em
from utils.statistics import send_confirm_mail, send_admin_statistics


@dp.message_handler(IsAdminMessage(), state=AddAdmin.Email)
async def update_email(message: types.Message, state: FSMContext):
    """Обновляем email"""
    email = message.text
    name = await db.get_admin_data(message.from_user.id)
    try:
        send_confirm_mail('Уведомление о привязке почты',
                          f'Пользователь {name} привязал этот email-адрес для получения статистики.',
                          email)
        await db.update_email_admin(email, message.from_user.id)
        await message.answer(f'{success_em} E-mail адрес {email} успешно привязан.')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получилось привязать E-mail адрес {email}.\n'
                             f'Проверьте правильность и введите адрес еще раз.')


@dp.callback_query_handler(text='cancel', state=AddAdmin.Statistics)
async def cancel(call: CallbackQuery):
    """Отмена"""
    await call.message.edit_reply_markup()
    await call.message.answer("Вы отменили операцию.")


@dp.callback_query_handler(text='back_to_location_statistics', state="*")
async def back_to_location_statistics(call: CallbackQuery):
    """Назад"""
    await call.message.edit_reply_markup()
    locations = await db.get_all_locations()
    await call.message.answer('Выберите локацию, по которой хотите получить статистику',
                              reply_markup=await generate_locations_keyboard(locations))


@dp.callback_query_handler(statistics_location_data.filter(location_id='all_locations'))
async def show_statistics_keyboard(call: CallbackQuery, state: FSMContext):
    """Показываем клавиатуру с выбором периода статистики"""
    await call.message.edit_reply_markup()
    await call.message.answer('Теперь выберите период',
                              reply_markup=admin_period_markup)
    await state.finish()


@dp.callback_query_handler(statistics_location_data.filter())
async def get_date(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer('Теперь выберите период',
                              reply_markup=period_markup)
    await state.update_data(location_id=(int(callback_data['location_id'])))
    await AddAdmin.Statistics.set()



@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='all_time'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за все время на {datetime.now(timezone("Europe/Moscow")).strftime("%d.%m.%Y")}'

    try:
        os.makedirs(f"{path_to_dir}")
    except Exception as err:
        logging.error(err)

    data = {
        'user_id': call.from_user.id,
        'to_email': email,
        'first_period': await db.get_first_order_date_admin(),
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


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='today'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow"))
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за {day.strftime("%d.%m.%Y")}'

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

        'orders': await db.get_orders_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'products': list(await db.get_order_products_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                        day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(day.strftime("%Y-%m-%d"),
                                                                       day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(day.strftime("%Y-%m-%d"),
                                                                                   day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                         day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                      day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                           day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='yesterday'))
async def get_all_statistics(call: CallbackQuery):
    """Получаем статистику по всем локациям"""
    day = datetime.now(timezone("Europe/Moscow")) - timedelta(days=1)
    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за {day.strftime("%d.%m.%Y")}'

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

        'orders': await db.get_orders_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'products': list(await db.get_order_products_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                        day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(day.strftime("%Y-%m-%d"),
                                                                       day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(day.strftime("%Y-%m-%d"),
                                                                                   day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                         day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                      day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(day.strftime("%Y-%m-%d"),
                                                                           day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='this_week'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за текущую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='last_week'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за прошедшую неделю ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='this_month'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за текущий месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='last_month'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за прошедший месяц ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='this_year'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за текущий год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='last_year'))
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за прошедший год ({first_day.strftime("%d.%m.%Y")}-{last_day.strftime("%d.%m.%Y")})'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)


@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='by_years'))
async def get_statistics(call: CallbackQuery, state: FSMContext):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await AddAdmin.Year.set()

@dp.callback_query_handler(text='back_to_statistics', state=[AddAdmin.Year,
                                                             AddAdmin.Month,
                                                             AddAdmin.Day])
async def back_from_year(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите период врмени, за который хотите получить статистику.',
                              reply_markup=admin_period_markup)
    await state.finish()


@dp.callback_query_handler(statistics_year_data.filter(), state=AddAdmin.Year)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Получаем статистику по году"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])

    last_day = datetime(year, 12, 31)
    first_day = datetime(year, 1, 1)

    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за {year} год'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)



@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=AddAdmin.Month)
@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='by_months'))
async def get_statistics(call: CallbackQuery):
    """Статистика по годам"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await AddAdmin.Month.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=AddAdmin.Month)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц, за который хотите получить статистику.",
                              reply_markup=await gen_months_keyboard(year, months))


@dp.callback_query_handler(statistics_year_month_data.filter(), state=AddAdmin.Month)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Показываем статистику за месяц и год"""
    year = int(callback_data["year"])
    month = int(callback_data["month"])

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    first_day = datetime(year, month, 1)

    email = await db.get_email_admin(call.from_user.id)
    await call.message.answer("Собираю статистику\n"
                              f"Она будет отправлена Вам на e-mail: {email}\n"
                              f"{warning_em} Это может занять несколько минут. Я отправлю Вам уведомление "
                              f"когда статистика будет отправлена")
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за {months_names[month]} {year} года'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)



@dp.callback_query_handler(statistics_date_data.filter(period='by_months'), state=AddAdmin.Day)
@dp.callback_query_handler(admin_statistics_date_data_all.filter(period='by_days'))
async def get_statistics(call: CallbackQuery):
    """Статистика по дням"""
    await call.message.edit_reply_markup()
    years = await db.get_orders_years()
    await call.message.answer('Выберите год',
                              reply_markup=await gen_years_keyboard(years))
    await AddAdmin.Day.set()


@dp.callback_query_handler(statistics_year_data.filter(), state=AddAdmin.Day)
async def get_year(call: CallbackQuery, callback_data: dict):
    """Предлагаем выбрать месяц"""
    await call.message.edit_reply_markup()
    year = int(callback_data["year"])
    months = await db.get_orders_months(year)
    await call.message.answer("Выберите месяц",
                              reply_markup=await gen_months_keyboard(year, months))


@dp.callback_query_handler(statistics_year_month_data.filter(), state=AddAdmin.Day)
async def get_month(call: CallbackQuery, callback_data: dict):
    """Получаем месяц"""
    year = int(callback_data["year"])
    month = int(callback_data["month"])
    days = await db.get_orders_days(year, month)
    await call.message.answer("Выберите день, за который хотите получить статистику.",
                              reply_markup=await gen_days_keyboard(days, year))


@dp.callback_query_handler(statistics_day_data.filter(), state=AddAdmin.Day)
async def get_statistics_by_day(call: CallbackQuery, callback_data: dict):
    """Статистика за день"""
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
    path_to_dir = f'statistics/all'
    file_name = f'Статистика по всем точкам продаж за {last_day.strftime("%d.%m.%Y")}'

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

        'orders': await db.get_orders_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'products': list(
            await db.get_order_products_admin_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))),
        'numbers': await db.get_orders_count_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                           last_day.strftime("%Y-%m-%d")),

        'indicators': await db.get_indicators_by_date(first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")),
        'bonus_indicators': await db.get_bonus_indicators_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                        last_day.strftime("%Y-%m-%d")),
        'indicators_by_loc': await db.get_admin_indicators_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                       last_day.strftime("%Y-%m-%d")),
        'bonus_indicators_by_loc': await db.get_bonus_indicators_admin_by_loc_date(first_day.strftime("%Y-%m-%d"),
                                                                                   last_day.strftime("%Y-%m-%d")),

        'bonus_orders': await db.get_bonus_orders_by_date(first_day.strftime("%Y-%m-%d"),
                                                          last_day.strftime("%Y-%m-%d")),

        'sellers_orders': await db.get_sellers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                    last_day.strftime("%Y-%m-%d")),
        'sellers_bonus': await db.get_sellers_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                         last_day.strftime("%Y-%m-%d")),

        'couriers_orders': await db.get_couriers_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                      last_day.strftime("%Y-%m-%d")),

        'user_orders': await db.get_users_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                               last_day.strftime("%Y-%m-%d")),
        'user_bonus_orders': await db.get_users_bonus_orders_admin_by_date(first_day.strftime("%Y-%m-%d"),
                                                                           last_day.strftime("%Y-%m-%d")),

    }

    await send_admin_statistics(data)