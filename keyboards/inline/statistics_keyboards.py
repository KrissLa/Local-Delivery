from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_datas import statistics_date_data, statistics_year_data, statistics_year_month_data, \
    statistics_day_data
from utils.pagination import add_pagination

months_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                'Ноябрь', 'Декабрь']

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
