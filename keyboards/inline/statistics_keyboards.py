import logging
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_datas import statistics_date_data, statistics_year_data, statistics_year_month_data, \
    statistics_day_data, statistics_location_data, admin_statistics_date_data_all, statistics_location_data_del, \
    statistics_date_delivery, statistics_delivery_year_data, statistics_delivery_year_month_data, \
    statistics_delivery_day_data, statistics_date_location_delivery, statistics_year_location_data, \
    statistics_delivery_year_month_loc_data, statistics_delivery_day_loc_data
from utils.pagination import add_pagination

months_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                'Ноябрь', 'Декабрь']

all_locations_button = InlineKeyboardButton(text='Все локации',
                                            callback_data=statistics_location_data.new(location_id='all_locations'))

all_delivery_locations_button = InlineKeyboardButton(text='Все локации',
                                                     callback_data=statistics_location_data_del.new(
                                                         location_id='all_locations'))


async def generate_locations_keyboard(locations, page=0):
    if len(locations) < 11:
        keyboard = InlineKeyboardMarkup()
        if page == 0:
            keyboard.add(all_locations_button)
        for location in locations:
            button = InlineKeyboardButton(
                text=location['location_name'],
                callback_data=statistics_location_data.new(location_id=location['location_id'])
            )
            keyboard.add(button)
    else:
        buttons_list = []
        if page == 0:
            buttons_list.append(all_locations_button)
        for location in locations:
            button = InlineKeyboardButton(
                text=location['location_name'],
                callback_data=statistics_location_data.new(location_id=location['location_id'])
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return keyboard


async def generate_locations_keyboard_del(locations, page=0):
    if len(locations) < 11:
        keyboard = InlineKeyboardMarkup()
        if page == 0:
            keyboard.add(all_delivery_locations_button)
        for location in locations:
            button = InlineKeyboardButton(
                text=location['location_name'],
                callback_data=statistics_location_data_del.new(location_id=location['location_id'])
            )
            keyboard.add(button)
    else:
        buttons_list = []
        if page == 0:
            buttons_list.append(all_locations_button)
        for location in locations:
            button = InlineKeyboardButton(
                text=location['location_name'],
                callback_data=statistics_location_data_del.new(location_id=location['location_id'])
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return keyboard


async def generate_delivery_period_keyboard(location_id, admin=True):
    logging.info(admin)
    back_button = InlineKeyboardButton(
        text='Назад',
        callback_data='back_to_loc'
    )
    cancel_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancek_delivery_stat'
    )
    delivery_period_location_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='За все время',
                callback_data=statistics_date_location_delivery.new(period='all_time', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За сегодня',
                callback_data=statistics_date_location_delivery.new(period='today', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За вчера',
                callback_data=statistics_date_location_delivery.new(period='yesterday', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За текущую неделю',
                callback_data=statistics_date_location_delivery.new(period='this_week', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За прошедшую неделю',
                callback_data=statistics_date_location_delivery.new(period='last_week', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За текущий месяц',
                callback_data=statistics_date_location_delivery.new(period='this_month', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За прошедший месяц',
                callback_data=statistics_date_location_delivery.new(period='last_month', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За текущий год',
                callback_data=statistics_date_location_delivery.new(period='this_year', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='За прошедший год',
                callback_data=statistics_date_location_delivery.new(period='last_year', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='По дням',
                callback_data=statistics_date_location_delivery.new(period='by_days', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='По месяцам',
                callback_data=statistics_date_location_delivery.new(period='by_months', location_id=location_id,
                                                                    admin=admin)
            )
        ],
        [
            InlineKeyboardButton(
                text='По годам',
                callback_data=statistics_date_location_delivery.new(period='by_years', location_id=location_id,
                                                                    admin=admin)
            )
        ]
    ])
    if admin:
        delivery_period_location_markup.add(back_button)
    else:
        delivery_period_location_markup.add(cancel_button)
    return delivery_period_location_markup


delivery_period_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='За все время',
            callback_data=statistics_date_delivery.new(period='all_time')
        )
    ],
    [
        InlineKeyboardButton(
            text='За сегодня',
            callback_data=statistics_date_delivery.new(period='today')
        )
    ],
    [
        InlineKeyboardButton(
            text='За вчера',
            callback_data=statistics_date_delivery.new(period='yesterday')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущую неделю',
            callback_data=statistics_date_delivery.new(period='this_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедшую неделю',
            callback_data=statistics_date_delivery.new(period='last_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий месяц',
            callback_data=statistics_date_delivery.new(period='this_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший месяц',
            callback_data=statistics_date_delivery.new(period='last_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий год',
            callback_data=statistics_date_delivery.new(period='this_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший год',
            callback_data=statistics_date_delivery.new(period='last_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='По дням',
            callback_data=statistics_date_delivery.new(period='by_days')
        )
    ],
    [
        InlineKeyboardButton(
            text='По месяцам',
            callback_data=statistics_date_delivery.new(period='by_months')
        )
    ],
    [
        InlineKeyboardButton(
            text='По годам',
            callback_data=statistics_date_delivery.new(period='by_years')
        )
    ],
    [
        InlineKeyboardButton(
            text='Назад',
            callback_data='back_to_loc'
        )
    ]
])

period_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='За все время',
            callback_data=statistics_date_data.new(period='all_time')
        )
    ],
    [
        InlineKeyboardButton(
            text='За сегодня',
            callback_data=statistics_date_data.new(period='today')
        )
    ],
    [
        InlineKeyboardButton(
            text='За вчера',
            callback_data=statistics_date_data.new(period='yesterday')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущую неделю',
            callback_data=statistics_date_data.new(period='this_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедшую неделю',
            callback_data=statistics_date_data.new(period='last_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий месяц',
            callback_data=statistics_date_data.new(period='this_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший месяц',
            callback_data=statistics_date_data.new(period='last_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий год',
            callback_data=statistics_date_data.new(period='this_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший год',
            callback_data=statistics_date_data.new(period='last_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='По дням',
            callback_data=statistics_date_data.new(period='by_days')
        )
    ],
    [
        InlineKeyboardButton(
            text='По месяцам',
            callback_data=statistics_date_data.new(period='by_months')
        )
    ],
    [
        InlineKeyboardButton(
            text='По годам',
            callback_data=statistics_date_data.new(period='by_years')
        )
    ],
    [
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel_statistics'
        )
    ]
])

admin_period_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='За все время',
            callback_data=admin_statistics_date_data_all.new(period='all_time')
        )
    ],
    [
        InlineKeyboardButton(
            text='За сегодня',
            callback_data=admin_statistics_date_data_all.new(period='today')
        )
    ],
    [
        InlineKeyboardButton(
            text='За вчера',
            callback_data=admin_statistics_date_data_all.new(period='yesterday')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущую неделю',
            callback_data=admin_statistics_date_data_all.new(period='this_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедшую неделю',
            callback_data=admin_statistics_date_data_all.new(period='last_week')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий месяц',
            callback_data=admin_statistics_date_data_all.new(period='this_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший месяц',
            callback_data=admin_statistics_date_data_all.new(period='last_month')
        )
    ],
    [
        InlineKeyboardButton(
            text='За текущий год',
            callback_data=admin_statistics_date_data_all.new(period='this_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='За прошедший год',
            callback_data=admin_statistics_date_data_all.new(period='last_year')
        )
    ],
    [
        InlineKeyboardButton(
            text='По дням',
            callback_data=admin_statistics_date_data_all.new(period='by_days')
        )
    ],
    [
        InlineKeyboardButton(
            text='По месяцам',
            callback_data=admin_statistics_date_data_all.new(period='by_months')
        )
    ],
    [
        InlineKeyboardButton(
            text='По годам',
            callback_data=admin_statistics_date_data_all.new(period='by_years')
        )
    ],
    [
        InlineKeyboardButton(
            text='Назад',
            callback_data='back_to_location_statistics'
        )
    ]
])


async def gen_years_keyboard(years, page=0):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    if len(years) < 11:
        for year in years:
            button = InlineKeyboardButton(
                text=f'{year["order_year"]}',
                callback_data=statistics_year_data.new(year=year["order_year"])
            )
            keyboard.add(button)
    else:
        buttons_list = []
        for year in years:
            button = InlineKeyboardButton(
                text=f'{year["order_year"]}',
                callback_data=statistics_year_data.new(year=year["order_year"])
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_statistics'))
    return keyboard


async def gen_delivery_loc_years_keyboard(years, location_id, admin=True, page=0):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    logging.info(admin)
    if len(years) < 11:
        for year in years:
            button = InlineKeyboardButton(
                text=f'{int(year["delivery_year"])}',
                callback_data=statistics_year_location_data.new(year=int(year["delivery_year"]),
                                                                location_id=location_id,
                                                                admin=admin)
            )
            keyboard.add(button)
    else:
        buttons_list = []
        for year in years:
            button = InlineKeyboardButton(
                text=f'{int(year["delivery_year"])}',
                callback_data=statistics_year_location_data.new(year=int(year["delivery_year"]),
                                                                location_id=location_id,
                                                                admin=admin)
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    if admin in [True, 'True']:
        keyboard.add(InlineKeyboardButton(text='Назад',
                                          callback_data=statistics_location_data_del.new(location_id=location_id)))
    else:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_statistics_seller'))
    return keyboard


async def gen_delivery_years_keyboard(years, page=0):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    if len(years) < 11:
        for year in years:
            button = InlineKeyboardButton(
                text=f'{int(year["delivery_year"])}',
                callback_data=statistics_delivery_year_data.new(year=int(year["delivery_year"]))
            )
            keyboard.add(button)
    else:
        buttons_list = []
        for year in years:
            button = InlineKeyboardButton(
                text=f'{int(year["delivery_year"])}',
                callback_data=statistics_delivery_year_data.new(year=int(year["delivery_year"]))
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_del_stat'))
    return keyboard


async def gen_months_keyboard(year, months):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    for month in months:
        button = InlineKeyboardButton(
            text=f'{months_names[month["order_month"]]}',
            callback_data=statistics_year_month_data.new(year=year, month=month["order_month"])
        )
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=statistics_date_data.new(period='by_months')))
    return keyboard


async def gen_delivery_months_keyboard(year, months, location_id, admin):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    for month in months:
        button = InlineKeyboardButton(
            text=f'{months_names[int(month["delivery_month"])]}',
            callback_data=statistics_delivery_year_month_loc_data.new(year=year,
                                                                      month=int(month["delivery_month"]),
                                                                      location_id=location_id,
                                                                      admin=admin)
        )
        keyboard.add(button)
        keyboard.add(
            InlineKeyboardButton(text='Назад', callback_data=statistics_date_location_delivery.new(period='this_month',
                                                                                                   location_id=location_id,
                                                                                                   admin=admin)))
    return keyboard


async def gen_delivery_months_loc_keyboard(year, months, location_id, admin=True):
    """Клавиатура с годами"""
    keyboard = InlineKeyboardMarkup()
    for month in months:
        button = InlineKeyboardButton(
            text=f'{months_names[int(month["delivery_month"])]}',
            callback_data=statistics_delivery_year_month_data.new(year=year, month=int(month["delivery_month"]))
        )
        keyboard.add(button)
    keyboard.add(
        InlineKeyboardButton(text='Назад', callback_data=statistics_date_location_delivery.new(period='this_month',
                                                                                               location_id=location_id,
                                                                                               admin=admin)))
    return keyboard


async def gen_days_keyboard(days, year):
    """Клавиатура с годами"""
    inline_keyb = []
    max = len(days)
    num = 1
    line_list = []
    for day in days:
        button = InlineKeyboardButton(
            text=f'{day["order_date"].strftime("%d.%m.%Y")}',
            callback_data=statistics_day_data.new(day=day["order_date"].strftime("%d"),
                                                  month=day["order_date"].strftime("%m"),
                                                  year=day["order_date"].strftime("%Y"))
        )
        line_list.append(button)
        if num % 3 == 0:
            inline_keyb.append(line_list)
            line_list = []
        elif num == max:
            inline_keyb.append(line_list)
        num += 1
    keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=inline_keyb)
    keyboard.add(
        InlineKeyboardButton(text='Назад', callback_data=statistics_year_data.new(year=year)))
    return keyboard


async def gen_delivery_days_keyboard(days, month, year):
    """Клавиатура с годами"""
    inline_keyb = []
    max = len(days)
    num = 1
    line_list = []
    for day in days:
        day_ = datetime(year, month, int(day["delivery_day"]))
        button = InlineKeyboardButton(
            text=f'{day_.strftime("%d.%m.%Y")}',
            callback_data=statistics_delivery_day_data.new(day=int(day["delivery_day"]),
                                                           month=month,
                                                           year=year)
        )
        line_list.append(button)
        if num % 3 == 0:
            inline_keyb.append(line_list)
            line_list = []
        elif num == max:
            inline_keyb.append(line_list)
        num += 1
    keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=inline_keyb)
    keyboard.add(
        InlineKeyboardButton(text='Назад', callback_data=statistics_delivery_year_data.new(year=year)))
    return keyboard


async def gen_delivery_days_keyboard_loc(days, month, year, location_id, admin):
    """Клавиатура с годами"""
    inline_keyb = []
    max = len(days)
    num = 1
    line_list = []
    for day in days:
        day_ = datetime(year, month, int(day["delivery_day"]))
        button = InlineKeyboardButton(
            text=f'{day_.strftime("%d.%m.%Y")}',
            callback_data=statistics_delivery_day_loc_data.new(day=int(day["delivery_day"]),
                                                               month=month,
                                                               year=year,
                                                               location_id=location_id,
                                                               admin=admin)
        )
        line_list.append(button)
        if num % 3 == 0:
            inline_keyb.append(line_list)
            line_list = []
        elif num == max:
            inline_keyb.append(line_list)
        num += 1
    keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=inline_keyb)
    keyboard.add(
        InlineKeyboardButton(text='Назад', callback_data=statistics_year_location_data.new(year=year,
                                                                                           location_id=location_id,
                                                                                           admin=admin)))
    return keyboard
