from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_datas import metro_data, categories_data, product_list_data, \
    product_count_price_data, local_object_data, deliver_to_time_data, size_product_data, back_to_product_list_data, \
    back_to_size_from_price_list_data, need_pass_data, couriers_data, active_order_data, active_bonus_order_data, \
    admin_data, metro_del_data, location_data, new_item_size, edit_item_data
from loader import db

back_button = InlineKeyboardButton(text='Назад', callback_data='back')
back_menu_button = InlineKeyboardButton(text='Назад', callback_data='back_main')

cancel_order_button = InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_order')
cancel_bonus_order_button = InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_bonus_order')

cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')


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


async def generate_keyboard_with_metro():
    """Генерируем клавиатуру со станциями метро"""
    list_of_metro = await db.get_available_metro()
    metro_markup = InlineKeyboardMarkup()
    for metro in list_of_metro:
        button = InlineKeyboardButton(
            text=metro['metro_name'],
            callback_data=metro_data.new(metro_id=metro['metro_id'])
        )
        metro_markup.add(button)
    return metro_markup


async def generate_keyboard_with_metro_profile():
    """Генерируем клавиатуру со станциями метро"""
    list_of_metro = await db.get_available_metro()
    print(list_of_metro)
    metro_markup = InlineKeyboardMarkup()
    if list_of_metro:
        for metro in list_of_metro:
            button = InlineKeyboardButton(
                text=metro['metro_name'],
                callback_data=metro_data.new(metro_id=metro['metro_id'])
            )
            metro_markup.add(button)
    metro_markup.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    # print(metro_markup)
    return metro_markup


async def get_available_local_objects(metro_id):
    """Генерируем клавиатуру с локациями"""
    list_of_local_objects = await db.get_available_local_objects(metro_id)

    local_objects_markup = InlineKeyboardMarkup()
    if list_of_local_objects:
        for local in list_of_local_objects:
            button = InlineKeyboardButton(
                text=local['local_object_name'],
                callback_data=local_object_data.new(local_object_id=local['local_object_id'])
            )
            local_objects_markup.add(button)
    else:
        local_objects_markup.add(back_button)
    return local_objects_markup


async def get_available_local_objects_profile(metro_id):
    """Генерируем клавиатуру с локациями"""
    list_of_local_objects = await db.get_available_local_objects(metro_id)

    local_objects_markup = InlineKeyboardMarkup()
    if list_of_local_objects:
        for local in list_of_local_objects:
            button = InlineKeyboardButton(
                text=local['local_object_name'],
                callback_data=local_object_data.new(local_object_id=local['local_object_id'])
            )
            local_objects_markup.add(button)
    local_objects_markup.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return local_objects_markup


async def generate_keyboard_with_categories(categories):
    """Генерируем клавиатуру с категориями"""

    categories_markup = InlineKeyboardMarkup()
    for cat in categories:
        button = InlineKeyboardButton(
            text=cat['category_name'],
            callback_data=categories_data.new(category_id=cat['category_id'])
        )
        categories_markup.add(button)
    categories_markup.add(back_menu_button)
    return categories_markup


async def generate_keyboard_with_none_categories():
    """Генерируем клавиатуру с категориями"""
    categories_markup = InlineKeyboardMarkup()
    categories_markup.add(back_menu_button)
    return categories_markup


async def generate_keyboard_with_products(products):
    """Генерируем клавиатуру с товарами"""

    products_markup = InlineKeyboardMarkup(row_width=1)
    for prod in products:
        button = InlineKeyboardButton(
            text=prod['product_name'],
            callback_data=product_list_data.new(product_id=prod['product_id'])
        )
        products_markup.add(button)
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


async def generate_key_board_with_admins():
    """Клавиатура для удаления админов"""
    admin_list = await db.get_all_admin()
    admin_keyboard = InlineKeyboardMarkup()
    for admin in admin_list:
        button = InlineKeyboardButton(
            text=f'{admin["admin_id"]}, {admin["admin_name"]}',
            callback_data=admin_data.new(admin_id=admin["admin_id"])
        )
        admin_keyboard.add(button)
    admin_keyboard.add(cancel_button)
    return admin_keyboard


async def generate_key_board_with_metro():
    """Клавиатура для удаления метро"""
    metro_list = await db.get_all_metro()
    admin_keyboard = InlineKeyboardMarkup()
    for metro in metro_list:
        button = InlineKeyboardButton(
            text=f'{metro["metro_id"]}, {metro["metro_name"]}',
            callback_data=metro_del_data.new(metro_id=metro["metro_id"])
        )
        admin_keyboard.add(button)
    admin_keyboard.add(cancel_button)
    return admin_keyboard


async def generate_keyboard_with_metro_for_seller_admin():
    """Клавиатура для удаления метро"""
    metro_list = await db.get_all_metro()
    admin_keyboard = InlineKeyboardMarkup()
    for metro in metro_list:
        button = InlineKeyboardButton(
            text=f'{metro["metro_id"]}, {metro["metro_name"]}',
            callback_data=metro_del_data.new(metro_id=metro["metro_id"])
        )
        admin_keyboard.add(button)
    admin_keyboard.add(InlineKeyboardButton(text='Позже', callback_data='seller_admin_later'))
    admin_keyboard.add(cancel_button)
    return admin_keyboard


async def generate_key_board_with_locations(metro_id):
    """Клавиатура с выбором локации"""
    location_list = await db.get_locations_by_metro_id(metro_id)
    location_keyboard = InlineKeyboardMarkup()
    for loc in location_list:
        button = InlineKeyboardButton(
            text=loc['location_name'],
            callback_data=location_data.new(location_id=loc['location_id'])
        )
        location_keyboard.add(button)
    location_keyboard.add(cancel_button)
    return location_keyboard


async def generate_keyboard_with_categories_for_add_item(categories):
    """Генерируем клавиатуру с категориями"""

    categories_markup = InlineKeyboardMarkup()
    for cat in categories:
        button = InlineKeyboardButton(
            text=cat['category_name'],
            callback_data=categories_data.new(category_id=cat['category_id'])
        )
        categories_markup.add(button)
    categories_markup.add(cancel_button)
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

cart_markup = InlineKeyboardMarkup(
    inline_keyboard=[
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

cancel_admin_markup = InlineKeyboardMarkup(inline_keyboard=[
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
