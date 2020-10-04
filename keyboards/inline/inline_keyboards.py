import logging
from datetime import datetime, timedelta, time, date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone

from keyboards.inline.callback_datas import metro_data, categories_data, product_list_data, \
    product_count_price_data, local_object_data, deliver_to_time_data, size_product_data, back_to_product_list_data, \
    back_to_size_from_price_list_data, need_pass_data, couriers_data, active_order_data, active_bonus_order_data, \
    admin_data, metro_del_data, location_data, new_item_size, edit_item_data, cancel_order_data, \
    delivery_categories_data, delivery_product_data, delivery_product_count_data, delivery_date_data, \
    delivery_time_data, take_delivery_order, dont_take_delivery_order, confirm_delivery_order
from loader import db
from utils.pagination import add_pagination
from utils.temp_orders_list import get_formatted_date

back_button = InlineKeyboardButton(text='Назад', callback_data='back')
back_menu_button = InlineKeyboardButton(text='Назад', callback_data='back_main')

cancel_order_button = InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_order')
cancel_bonus_order_button = InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_bonus_order')

cancel_button = InlineKeyboardButton(text='Отмена/Готово', callback_data='cancel')


async def generate_key_board_with_admins(page=0):
    """Клавиатура для удаления админов"""
    admin_list = await db.get_all_admin()
    admin_keyboard = InlineKeyboardMarkup()
    if len(admin_list) < 11:
        for admin in admin_list:
            button = InlineKeyboardButton(
                text=f'{admin["admin_id"]}, {admin["admin_name"]}',
                callback_data=admin_data.new(admin_id=admin["admin_id"])
            )
            admin_keyboard.add(button)
    else:
        buttons_list = []
        for admin in admin_list:
            button = InlineKeyboardButton(
                text=f'{admin["admin_id"]}, {admin["admin_name"]}',
                callback_data=admin_data.new(admin_id=admin["admin_id"])
            )
            buttons_list.append([button])
        admin_keyboard = await add_pagination(buttons_list, page)
    admin_keyboard.add(cancel_button)
    return admin_keyboard


async def generate_couriers_keyboard(couriers, order_id):
    """Формируем клавиатуру с курьерами"""
    couriers_keyboard = InlineKeyboardMarkup()
    for cour in couriers:
        button = InlineKeyboardButton(
            text=cour['courier_name'],
            callback_data=couriers_data.new(courier_tg_id=cour['courier_telegram_id'], order_id=order_id)
        )
        couriers_keyboard.add(button)
    return couriers_keyboard


async def generate_keyboard_with_metro_for_seller_admin(page=0):
    """Клавиатура для удаления метро"""
    metro_list = await db.get_all_metro()
    admin_keyboard = InlineKeyboardMarkup()
    if len(metro_list) < 11:
        for metro in metro_list:
            button = InlineKeyboardButton(
                text=f'{metro["metro_id"]}, {metro["metro_name"]}',
                callback_data=metro_del_data.new(metro_id=metro["metro_id"])
            )
            admin_keyboard.add(button)
    else:
        buttons_list = []
        for metro in metro_list:
            button = InlineKeyboardButton(
                text=f'{metro["metro_id"]}, {metro["metro_name"]}',
                callback_data=metro_del_data.new(metro_id=metro["metro_id"])
            )
            buttons_list.append([button])
        admin_keyboard = await add_pagination(buttons_list, page)
    admin_keyboard.add(InlineKeyboardButton(text='Позже', callback_data='seller_admin_later'))
    admin_keyboard.add(cancel_button)
    return admin_keyboard


async def generate_key_board_with_metro(page=0):
    """Клавиатура для удаления метро"""
    metro_list = await db.get_all_metro()
    keyboard = InlineKeyboardMarkup()
    if len(metro_list) < 11:
        for metro in metro_list:
            button = InlineKeyboardButton(
                text=f'{metro["metro_id"]}, {metro["metro_name"]}',
                callback_data=metro_del_data.new(metro_id=metro["metro_id"])
            )
            keyboard.add(button)
    else:
        buttons_list = []
        for metro in metro_list:
            button = InlineKeyboardButton(
                text=f'{metro["metro_id"]}, {metro["metro_name"]}',
                callback_data=metro_del_data.new(metro_id=metro["metro_id"])
            )
            buttons_list.append([button])
        keyboard = await add_pagination(buttons_list, page)
    keyboard.add(cancel_button)
    return keyboard


async def generate_keyboard_with_metro(page=0):
    """Генерируем клавиатуру со станциями метро"""
    list_of_metro = await db.get_available_metro()
    metro_markup = InlineKeyboardMarkup()
    if len(list_of_metro) < 11:
        for metro in list_of_metro:
            button = InlineKeyboardButton(
                text=metro['metro_name'],
                callback_data=metro_data.new(metro_id=metro['metro_id'])
            )
            metro_markup.add(button)
    else:
        buttons_list = []
        for metro in list_of_metro:
            button = InlineKeyboardButton(
                text=metro['metro_name'],
                callback_data=metro_data.new(metro_id=metro['metro_id'])
            )
            buttons_list.append([button])
        metro_markup = await add_pagination(buttons_list, page)
    return metro_markup


async def generate_keyboard_with_metro_profile(page=0):
    """Генерируем клавиатуру со станциями метро"""
    list_of_metro = await db.get_available_metro()
    metro_markup = InlineKeyboardMarkup()
    if list_of_metro:
        if len(list_of_metro) < 11:
            for metro in list_of_metro:
                button = InlineKeyboardButton(
                    text=metro['metro_name'],
                    callback_data=metro_data.new(metro_id=metro['metro_id'])
                )
                metro_markup.add(button)
        else:
            buttons_list = []
            for metro in list_of_metro:
                button = InlineKeyboardButton(
                    text=metro['metro_name'],
                    callback_data=metro_data.new(metro_id=metro['metro_id'])
                )
                buttons_list.append([button])
            metro_markup = await add_pagination(buttons_list, page)
    metro_markup.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return metro_markup


async def generate_key_board_with_locations(metro_id, page=0):
    """Клавиатура с выбором локации"""
    location_list = await db.get_locations_by_metro_id(metro_id)
    keyboard = InlineKeyboardMarkup()
    if len(location_list) < 11:
        for loc in location_list:
            button = InlineKeyboardButton(
                text=loc['location_name'],
                callback_data=location_data.new(location_id=loc['location_id'])
            )
            keyboard.add(button)
    else:
        buttons_list = []
        for loc in location_list:
            button = InlineKeyboardButton(
                text=loc['location_name'],
                callback_data=location_data.new(location_id=loc['location_id'])
            )
            buttons_list.append([button])
            keyboard = await add_pagination(buttons_list, page)
    keyboard.add(cancel_button)
    return keyboard


async def get_available_local_objects(metro_id, page=0):
    """Генерируем клавиатуру с локациями"""
    list_of_local_objects = await db.get_available_local_objects(metro_id)

    if list_of_local_objects:
        if len(list_of_local_objects) < 11:
            local_objects_markup = InlineKeyboardMarkup()
            for local in list_of_local_objects:
                button = InlineKeyboardButton(
                    text=local['local_object_name'],
                    callback_data=local_object_data.new(local_object_id=local['local_object_id'])
                )
                local_objects_markup.add(button)

        else:
            buttons_list = []
            for local in list_of_local_objects:
                button = InlineKeyboardButton(
                    text=local['local_object_name'],
                    callback_data=local_object_data.new(local_object_id=local['local_object_id'])
                )
                buttons_list.append([button])
            local_objects_markup = await add_pagination(buttons_list, page)
        local_objects_markup.add(back_button)
    else:
        local_objects_markup = InlineKeyboardMarkup()
        local_objects_markup.add(back_button)
    return local_objects_markup


async def get_available_local_objects_profile(metro_id, page=0):
    """Генерируем клавиатуру с локациями"""
    list_of_local_objects = await db.get_available_local_objects(metro_id)
    if len(list_of_local_objects) < 11:
        local_objects_markup = InlineKeyboardMarkup()
        if list_of_local_objects:
            for local in list_of_local_objects:
                button = InlineKeyboardButton(
                    text=local['local_object_name'],
                    callback_data=local_object_data.new(local_object_id=local['local_object_id'])
                )
                local_objects_markup.add(button)
    else:
        buttons_list = []
        for local in list_of_local_objects:
            button = InlineKeyboardButton(
                text=local['local_object_name'],
                callback_data=local_object_data.new(local_object_id=local['local_object_id'])
            )
            buttons_list.append([button])
        local_objects_markup = await add_pagination(buttons_list, page)
    local_objects_markup.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return local_objects_markup


async def generate_keyboard_with_categories_for_add_item(categories, page=0):
    """Генерируем клавиатуру с категориями"""
    if len(categories) < 11:
        categories_markup = InlineKeyboardMarkup()
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['category_name'],
                callback_data=categories_data.new(category_id=cat['category_id'])
            )
            categories_markup.add(button)
    else:
        buttons_list = []
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['category_name'],
                callback_data=categories_data.new(category_id=cat['category_id'])
            )
            buttons_list.append([button])
        categories_markup = await add_pagination(buttons_list, page)
    categories_markup.add(cancel_button)
    return categories_markup




async def generate_keyboard_with_delivery_categories_for_add_item(categories, page=0):
    """Генерируем клавиатуру с категориями"""
    if len(categories) < 11:
        categories_markup = InlineKeyboardMarkup()
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['delivery_category_name'],
                callback_data=categories_data.new(category_id=cat['delivery_category_id'])
            )
            categories_markup.add(button)
    else:
        buttons_list = []
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['delivery_category_name'],
                callback_data=categories_data.new(category_id=cat['delivery_category_id'])
            )
            buttons_list.append([button])
        categories_markup = await add_pagination(buttons_list, page)
    categories_markup.add(cancel_button)
    return categories_markup


async def generate_keyboard_with_categories(categories, page=0):
    """Генерируем клавиатуру с категориями"""
    if len(categories) < 11:
        categories_markup = InlineKeyboardMarkup()
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['category_name'],
                callback_data=categories_data.new(category_id=cat['category_id'])
            )
            categories_markup.add(button)
    else:
        buttons_list = []
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['category_name'],
                callback_data=categories_data.new(category_id=cat['category_id'])
            )
            buttons_list.append([button])
        categories_markup = await add_pagination(buttons_list, page)
    categories_markup.add(back_menu_button)
    return categories_markup


async def generate_keyboard_with_delivery_categories(categories, page=0, wbb=True):
    """Генерируем клавиатуру с категориями"""
    if len(categories) < 11:
        categories_markup = InlineKeyboardMarkup()
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['delivery_category_name'],
                callback_data=delivery_categories_data.new(category_id=cat['delivery_category_id'])
            )
            categories_markup.add(button)
    else:
        buttons_list = []
        for cat in categories:
            button = InlineKeyboardButton(
                text=cat['delivery_category_name'],
                callback_data=delivery_categories_data.new(category_id=cat['delivery_category_id'])
            )
            buttons_list.append([button])
        categories_markup = await add_pagination(buttons_list, page)
    if wbb:
        categories_markup.add(back_menu_button)
    return categories_markup


async def generate_keyboard_with_none_categories():
    """Генерируем клавиатуру с категориями"""
    categories_markup = InlineKeyboardMarkup()
    categories_markup.add(back_menu_button)
    return categories_markup


async def get_edit_item_markup(product_info):
    """Генерируем клавиатуру для изменения товара"""
    edit_item_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Название',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='name')
            )
        ],
        [
            InlineKeyboardButton(
                text='Описание',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='description')
            )
        ],
        [
            InlineKeyboardButton(
                text='Фотографию',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='photo')
            )
        ],
        [
            InlineKeyboardButton(
                text='Цены',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='prices')
            )
        ],
        [
            InlineKeyboardButton(
                text='Размеры',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='sizes')
            )
        ],
        [
            InlineKeyboardButton(
                text='Наличие в продаже',
                callback_data=edit_item_data.new(item_id=product_info['product_id'],
                                                 subject='available')
            )
        ],
        [
            cancel_button
        ]
    ])
    return edit_item_markup


async def generate_keyboard_with_products(products, page=0):
    """Генерируем клавиатуру с товарами"""
    if len(products) < 11:
        products_markup = InlineKeyboardMarkup(row_width=1)
        for prod in products:
            button = InlineKeyboardButton(
                text=prod['product_name'],
                callback_data=product_list_data.new(product_id=prod['product_id'])
            )
            products_markup.add(button)
    else:
        buttons_list = []
        for prod in products:
            button = InlineKeyboardButton(
                text=prod['product_name'],
                callback_data=product_list_data.new(product_id=prod['product_id'])
            )
            buttons_list.append([button])
        products_markup = await add_pagination(buttons_list, page)
    products_markup.add(back_button)
    return products_markup


async def generate_keyboard_with_delivery_products(products, page=0):
    """Генерируем клавиатуру с товарами"""
    if len(products) < 11:
        products_markup = InlineKeyboardMarkup(row_width=1)
        for prod in products:
            button = InlineKeyboardButton(
                text=prod['delivery_product_name'],
                callback_data=delivery_product_data.new(product_id=prod['delivery_product_id'],
                                                        price=prod['delivery_price'])
            )
            products_markup.add(button)
    else:
        buttons_list = []
        for prod in products:
            button = InlineKeyboardButton(
                text=prod['delivery_product_name'],
                callback_data=delivery_product_data.new(product_id=prod['delivery_product_id'],
                                                        price=prod['delivery_price'])
            )
            buttons_list.append([button])
        products_markup = await add_pagination(buttons_list, page)
    products_markup.add(back_button)
    return products_markup


async def generate_keyboard_with_products_for_remove_from_stock(products):
    """Генерируем клавиатуру с товарами"""

    products_markup = InlineKeyboardMarkup(row_width=1)
    for prod in products:
        button = InlineKeyboardButton(
            text=prod['product_name'],
            callback_data=product_list_data.new(product_id=prod['product_id'])
        )
        products_markup.add(button)
    products_markup.add(cancel_button)
    return products_markup


async def generate_keyboard_with_none_products():
    """Генерируем клавиатуру с товарами"""
    products_markup = InlineKeyboardMarkup(row_width=1)
    products_markup.add(back_button)
    return products_markup


async def generate_keyboard_with_sizes(sizes_list, category_id):
    """Генерируем клавиатуру с доступными размерами"""
    sizes_markup = InlineKeyboardMarkup()
    for size in sizes_list:
        button = InlineKeyboardButton(
            text=f"{size['size_name']} - {size['price_1']} руб",
            callback_data=size_product_data.new(size_id=size['size_id'], product_id=size['size_product_id'])
        )
        sizes_markup.add(button)
    sizes_markup.add(InlineKeyboardButton(
        text='Назад',
        callback_data=back_to_product_list_data.new(category_id=category_id)
    ))
    return sizes_markup


async def generate_keyboard_with_count_and_prices(product_info):
    """Генерируем клавиатуру с количеством товара и ценами"""
    products_count_price_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"1 по {product_info['price_1']} руб.",
                    callback_data=product_count_price_data.new(quantity=1,
                                                               price=product_info['price_1'])
                ),
                InlineKeyboardButton(
                    text=f"2 по {product_info['price_2']} руб.",
                    callback_data=product_count_price_data.new(quantity=2,
                                                               price=product_info['price_2'])
                ),
                InlineKeyboardButton(
                    text=f"3 по {product_info['price_3']} руб.",
                    callback_data=product_count_price_data.new(quantity=3,
                                                               price=product_info['price_3'])
                )
            ],

            [
                InlineKeyboardButton(
                    text=f"4 по {product_info['price_4']} руб.",
                    callback_data=product_count_price_data.new(quantity=4,
                                                               price=product_info['price_4'])
                ),
                InlineKeyboardButton(
                    text=f"5 по {product_info['price_5']} руб.",
                    callback_data=product_count_price_data.new(quantity=5,
                                                               price=product_info['price_5'])
                ),
                InlineKeyboardButton(
                    text=f"6+ по {product_info['price_6']} руб.",
                    callback_data=product_count_price_data.new(quantity=6,
                                                               price=product_info['price_6'])
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=back_to_product_list_data.new(category_id=product_info['product_category_id'])
                )
            ]
        ]
    )
    return products_count_price_markup


async def generate_keyboard_with_counts_for_delivery_products(price, category_id):
    """Генерируем клавиатуру с количеством и ценами"""
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'1 лоток (12шт.) - {price} руб.',
                    callback_data=delivery_product_count_data.new(quantity=1, price=price)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'2 лотка (24шт.) - {price * 2} руб.',
                    callback_data=delivery_product_count_data.new(quantity=2, price=price * 2)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'3 лотка (36шт.) - {price * 3} руб.',
                    callback_data=delivery_product_count_data.new(quantity=3, price=price * 3)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'4 лотка (48шт.) - {price * 4} руб.',
                    callback_data=delivery_product_count_data.new(quantity=4, price=price * 4)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'5 лотков (60шт.) - {price * 5} руб.',
                    callback_data=delivery_product_count_data.new(quantity=5, price=price * 5)
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'6 лотков и более',
                    callback_data=delivery_product_count_data.new(quantity='6+', price=price)
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=back_to_product_list_data.new(category_id=category_id)
                )
            ]
        ]
    )
    return markup


async def generate_keyboard_with_count_and_prices_for_size(size_info, product_id):
    """Генерируем клавиатуру с количеством товара и ценами"""
    products_count_price_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"1 по {size_info['price_1']} руб.",
                    callback_data=product_count_price_data.new(quantity=1,
                                                               price=size_info['price_1'])
                ),
                InlineKeyboardButton(
                    text=f"2 по {size_info['price_2']} руб.",
                    callback_data=product_count_price_data.new(quantity=2,
                                                               price=size_info['price_2'])
                ),
                InlineKeyboardButton(
                    text=f"3 по {size_info['price_3']} руб.",
                    callback_data=product_count_price_data.new(quantity=3,
                                                               price=size_info['price_3'])
                )
            ],

            [
                InlineKeyboardButton(
                    text=f"4 по {size_info['price_4']} руб.",
                    callback_data=product_count_price_data.new(quantity=4,
                                                               price=size_info['price_4'])
                ),
                InlineKeyboardButton(
                    text=f"5 по {size_info['price_5']} руб.",
                    callback_data=product_count_price_data.new(quantity=5,
                                                               price=size_info['price_5'])
                ),
                InlineKeyboardButton(
                    text=f"6+ по {size_info['price_6']} руб.",
                    callback_data=product_count_price_data.new(quantity=6,
                                                               price=size_info['price_6'])
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=back_to_size_from_price_list_data.new(product_id=product_id)
                )
            ]
        ]
    )
    return products_count_price_markup


async def build_keyboard_with_time(del_type, back_callback):
    """Строим клавиатуру"""
    deliver_to_time_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='10 мин',
                    callback_data=deliver_to_time_data.new(time=10, value='10 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='15 мин',
                    callback_data=deliver_to_time_data.new(time=15, value='15 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='20 мин',
                    callback_data=deliver_to_time_data.new(time=20, value='20 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='25 мин',
                    callback_data=deliver_to_time_data.new(time=25, value='25 минут', del_type=del_type)
                )
            ],
            [
                InlineKeyboardButton(
                    text='30 мин',
                    callback_data=deliver_to_time_data.new(time=30, value='30 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='40 мин',
                    callback_data=deliver_to_time_data.new(time=40, value='40 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='50 мин',
                    callback_data=deliver_to_time_data.new(time=50, value='50 минут', del_type=del_type)
                ),
                InlineKeyboardButton(
                    text='1 час',
                    callback_data=deliver_to_time_data.new(time=60, value='1 час', del_type=del_type)
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=back_callback
                )
            ],
            [
                cancel_order_button
            ]]

    )
    return deliver_to_time_markup


async def generate_active_order_keyboard(order):
    """Формируем клавиатуру для отметки готовности заказа"""
    active_orders_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Заказ готов',
                callback_data=active_order_data.new(order_id=order['order_id'],
                                                    delivery_method=order['delivery_method'],
                                                    user_id=order['order_user_telegram_id'])
            )
        ]
    ])

    return active_orders_keyboard


async def generate_active_bonus_order_keyboard(order):
    """Формируем клавиатуру для отметки готовности заказа"""
    active_orders_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Заказ готов',
                callback_data=active_bonus_order_data.new(order_id=order['bonus_order_id'],
                                                          user_id=order['bonus_order_user_telegram_id'])
            )
        ]
    ])

    return active_orders_keyboard


yes_and_cancel_admin_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Сохраняем',
            callback_data='save_newlocation'
        )
    ],
    [
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )
    ]

])

add_one_more_product_size = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Готово',
            callback_data='add_new_product_size_done'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавить еще один размер',
            callback_data='one_more_product_size'
        )
    ]

])

add_one_more_local_object = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Готово',
            callback_data='add_new_object_done'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавить еще один объект доставки',
            callback_data='one_more_object'
        )
    ]

])

add_one_more_category_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Готово',
            callback_data='add_new_category_done'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавить еще одину категорию',
            callback_data='one_more_category'
        )
    ]

])

item_with_size = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Да, добавим размеры',
            callback_data=new_item_size.new(status='True')
        )
    ],
    [
        InlineKeyboardButton(
            text='Нет, только один вариант',
            callback_data=new_item_size.new(status='False')
        )
    ],
    [
        cancel_button
    ]

])

confirm_item_markup_first = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Сохраняем',
            callback_data='save_item'
        )
    ],
    [
        InlineKeyboardButton(
            text='Назад к выбору количества размеров',
            callback_data='back'
        )
    ]

])

confirm_item_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Сохраняем',
            callback_data='save_item'
        )
    ],
    [
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )
    ]

])

back_to_choices_sizes = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Назад к выбору количества размеров',
            callback_data='back'
        )
    ]
])

cancel_admin_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )
    ]
])

back_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        back_button
    ]
])


async def add_delivery_order_markup(product_id, price):
    delivery_cart_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Оформить заказ',
                callback_data='registration_delivery_order'
            )
        ],
        [
            InlineKeyboardButton(
                text='Добавить другие позиции к заказу',
                callback_data='add_delivery_order'
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=delivery_product_data.new(
                    product_id=product_id,
                    price=price)
            )
        ]
    ])
    return delivery_cart_markup


cart_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='В меню продолжить покупки',
                callback_data='to_menu_one_more_product'
            )
        ],
        [
            InlineKeyboardButton(
                text='С доставкой',
                callback_data='delivery_option_delivery'
            )
        ],
        [
            InlineKeyboardButton(
                text='Заберу сам',
                callback_data='delivery_option_pickup'
            )
        ],
        [
            InlineKeyboardButton(
                text='Очистить корзину и отменить заказ',
                callback_data='cancel_order')
        ]
    ]
)

one_more_product_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='В меню продолжить покупки',
                callback_data='to_menu_one_more_product'
            )
        ]
    ])

delivery_options_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='В меню продолжить покупки',
                callback_data='to_menu_one_more_product'
            )
        ],
        [
            InlineKeyboardButton(
                text='С доставкой',
                callback_data='delivery_option_delivery'
            )
        ],
        [
            InlineKeyboardButton(
                text='Заберу сам',
                callback_data='delivery_option_pickup'
            )
        ],
        [
            back_button
        ],
        [
            cancel_order_button
        ]
    ]
)

need_pass_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Пропуск заказан',
                callback_data=need_pass_data.new(status=True)
            )
        ],
        [
            InlineKeyboardButton(
                text='Пропуск не требуется',
                callback_data=need_pass_data.new(status=False)
            )
        ],
        [
            back_button
        ],
        [
            cancel_order_button
        ]
    ]
)

order_cancel_or_back_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            back_button
        ],
        [
            cancel_order_button
        ]
    ]
)

confirm_order_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Оформить заказ',
                callback_data='confirm_order'
            )
        ],
        [
            back_button
        ],
        [
            cancel_order_button
        ]
    ]
)

back_cancel_bonus_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        back_button
    ],
    [
        cancel_bonus_order_button
    ]
])


async def cancel_order_by_use_button(order_id):
    """Отмена заказа пользователем"""

    cancel_order_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Отменить заказ',
                    callback_data=cancel_order_data.new(order_id=order_id)
                )
            ]
        ]
    )
    return cancel_order_markup


async def get_markup_with_date():
    """Генерируем клавиатуру с датами"""
    now = datetime.now(timezone("Europe/Moscow"))
    # now = datetime(2020, 12, 28, 20)
    logging.info(now)
    if now.hour < 17:
        logging.info('Попали в меньше 17')
        first_day = now
    else:
        logging.info('Попали в больше 17')
        first_day = now + timedelta(days=1)
    days = [await get_formatted_date(first_day, delta) for delta in range(1, 8)]
    logging.info(days)
    markup = InlineKeyboardMarkup()
    for day in days:
        button = InlineKeyboardButton(
            text=f'{day["date"]} {day["day"]}',
            callback_data=delivery_date_data.new(date=day['date'], weekday=day['day'])
        )
        markup.add(button)
    markup.add(back_button)
    logging.info(markup)
    return markup


async def get_markup_with_date_change(order_datetime):
    """Генерируем клавиатуру с датами"""
    if order_datetime.hour == 18:
        first_day = order_datetime + timedelta(days=1)

    else:
        first_day = order_datetime
    days = [await get_formatted_date(first_day, delta) for delta in range(0, 7)]
    markup = InlineKeyboardMarkup()
    for day in days:
        button = InlineKeyboardButton(
            text=f'{day["date"]} {day["day"]}',
            callback_data=delivery_date_data.new(date=day['date'], weekday=day['day'])
        )
        markup.add(button)
    markup.add(back_button)
    return markup


time_8_button = InlineKeyboardButton(
    text='с 08:00 до 10:00',
    callback_data=delivery_time_data.new(time=8, choice='c 08-00 до 10-00')
)

time_10_button = InlineKeyboardButton(
    text='с 10:00 до 12:00',
    callback_data=delivery_time_data.new(time=10, choice='с 10-00 до 12-00')
)

time_12_button = InlineKeyboardButton(
    text='с 12:00 до 14:00',
    callback_data=delivery_time_data.new(time=12, choice='с 12-00 до 14-00')
)

time_14_button = InlineKeyboardButton(
    text='с 14:00 до 16:00',
    callback_data=delivery_time_data.new(time=14, choice='с 14-00 до 16-00')
)

time_16_button = InlineKeyboardButton(
    text='с 16:00 до 18:00',
    callback_data=delivery_time_data.new(time=16, choice='с 16-00 до 18-00')
)

time_18_button = InlineKeyboardButton(
    text='с 18:00 до 20:00',
    callback_data=delivery_time_data.new(time=18, choice='с 18-00 до 20-00')
)


async def generate_time_markup(delivery_time):
    """Генерируем клавиатуру со временем"""
    if delivery_time == 'c 08-00 до 10-00':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                time_10_button
            ],
            [
                time_12_button
            ],
            [
                time_14_button
            ],
            [
                time_16_button
            ],
            [
                time_18_button
            ],
            [
                back_button
            ]
        ])
    elif delivery_time == 'с 10-00 до 12-00':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                time_12_button
            ],
            [
                time_14_button
            ],
            [
                time_16_button
            ],
            [
                time_18_button
            ],
            [
                back_button
            ]
        ])
    elif delivery_time == 'с 12-00 до 14-00':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                time_14_button
            ],
            [
                time_16_button
            ],
            [
                time_18_button
            ],
            [
                back_button
            ]
        ])
    elif delivery_time == 'с 14-00 до 16-00':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                time_16_button
            ],
            [
                time_18_button
            ],
            [
                back_button
            ]
        ])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                time_18_button
            ],
            [
                back_button
            ]
        ])
    return markup

time_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        time_8_button
    ],
    [
        time_10_button
    ],
    [
        time_12_button
    ],
    [
        time_14_button
    ],
    [
        time_16_button
    ],
    [
        time_18_button
    ],
    [
        back_button
    ]
])

confirm_delivery_order_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Подтвердить заказ',
            callback_data='confirm_delivery_order'
        )
    ],
    [
        InlineKeyboardButton(
            text='Отменить заказ',
            callback_data='cancel_delivery_order'
        )
    ],
    [
        back_button
    ]
])

confirm_changes_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Да, сохраняем изменения',
            callback_data='confirm_changes'
        )
    ],
    [
      InlineKeyboardButton(
          text='Отменить изменения',
          callback_data='cancel'
      )
    ],
    [
        back_button
    ]
])

change_delivery_order_button = InlineKeyboardButton(
    text='Изменить дату и время заказа',
    callback_data='change_delivery_time'
)

cancel_delivery_order_button = InlineKeyboardButton(
    text='Отменить заказ',
    callback_data='cancel_delivery_order'
)

confirm_cancel_delivery = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Да, отменить заказ',
            callback_data='confirm_cancel_delivery'
        )
    ],
    [
        back_button
    ]
])

change_delivery_order_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        change_delivery_order_button
    ],
    [
        back_button
    ]
])

change_and_cancel_delivery_order_markup = InlineKeyboardMarkup(inline_keyboard=[
    [
        change_delivery_order_button
    ],
    [
        cancel_delivery_order_button
    ],
    [
        back_button
    ]
])


async def gen_take_order_markup(order_id):
    take_delivery_order_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Принять',
                callback_data=take_delivery_order.new(order_id=order_id)
            )
        ],
        [
            InlineKeyboardButton(
                text='Отклонить',
                callback_data=dont_take_delivery_order.new(order_id=order_id)
            )
        ],
        [
            back_button
        ]
    ])
    return take_delivery_order_markup


async def gen_confirm_order_markup(order_id):
    take_delivery_order_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Заказ доставлен',
                callback_data=confirm_delivery_order.new(order_id=order_id)
            )
        ],
        [
            InlineKeyboardButton(
                text='Отклонить',
                callback_data=dont_take_delivery_order.new(order_id=order_id)
            )
        ],
        [
            back_button
        ]
    ])
    return take_delivery_order_markup

