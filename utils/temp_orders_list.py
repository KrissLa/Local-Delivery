import logging

from loader import db
from pytz import timezone
from datetime import datetime, timedelta

from utils.emoji import attention_em, warning_em, blue_diamond_em
from utils.product_list import get_delivery_product_list

weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


async def get_temp_orders_list_message(orders):
    """Формируем список покупок за сеанс"""
    mes = ''
    num = 1
    for order in orders:
        mes += f'   {num}. {order["product_name"]} - {order["quantity"]} шт. {order["order_price"]} руб.\n'
        num += 1
    return mes


async def get_temp_delivery_orders_list_message(orders):
    """Формируем список покупок за сеанс"""
    mes = ''
    num = 1
    for order in orders:
        items = order["delivery_quantity"] * 12
        digit = int(str(order["delivery_quantity"])[-1])
        if digit == 1 and order["delivery_quantity"] != 11:
            tray = 'лоток'
        elif digit in [2, 3, 4] and order["delivery_quantity"] not in [12, 13, 14]:
            tray = 'лотка'
        else:
            tray = 'лотков'
        mes += f'   {num}. {order["delivery_product_name"]} -\n    {order["delivery_quantity"]} ' \
               f'{tray} ({items} шт.) {order["delivery_order_price"]} руб.\n\n'
        num += 1
    return mes


async def get_objects_list_message(objects):
    """Формируем список объектов доставки"""
    mes = ''
    num = 1
    for ob in objects:
        mes += f'{num}. Москва, {ob["local_object_name"]}\n'
        num += 1
    return mes


async def get_final_price(orders):
    """Считаем окончательную цену"""
    fin_price = 0
    for order in orders:
        fin_price += order['order_price']
    return int(fin_price)


async def get_final_delivery_price(orders):
    """Считаем окончательную цену"""
    fin_price = 0
    for order in orders:
        fin_price += order['delivery_order_price']
    return int(fin_price)


async def get_couriers_list(couriers):
    """Формируем список курьеров"""
    mes = ''
    num = 1
    for cour in couriers:
        mes += f"   {num}. {cour['courier_name']}\n"
        num += 1
    return mes


async def get_list_of_location_message(list_of_locations):
    """Формируем список локаций для удаления"""
    mes = ''
    for loc in list_of_locations:
        metro_name = await db.get_metro_name_by_location_metro_id(loc['location_metro_id'])
        location = f"""{loc['location_id']}. {loc['location_name']}
Станция метро: {metro_name}
Адрес: {loc['location_address']}
Чтобы удалить нажмите /delete_location_{loc['location_id']}\n\n"""
        mes += location
    return mes


async def get_list_of_local_objects(local_objects_list):
    """Формируем список локаций для удаления"""
    mes = ''
    for loc in local_objects_list:
        local_objects = f"""{loc['local_object_id']}. {loc['local_object_name']}
Точка продаж: {loc['location_name']}
Адрес: {loc['location_address']}
Чтобы удалить нажмите /remove_local_object_{loc['local_object_id']}\n\n"""
        mes += local_objects
    return mes


async def get_list_of_category(category_list):
    """Формируем список локаций для удаления"""
    mes = ''

    for cat in category_list:
        count_products = await db.get_count_products(cat['category_id'])
        category = f"""{cat['category_id']}. {cat['category_name']}
Количество товаров в категории: {count_products}
Чтобы удалить нажмите /remove_category_by_id_{cat['category_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_delivery_category(category_list):
    """Формируем список локаций для удаления"""
    mes = ''

    for cat in category_list:
        count_products = await db.get_count_products_delivery(cat['delivery_category_id'])
        category = f"""{cat['delivery_category_id']}. {cat['delivery_category_name']}
Количество товаров в категории: {count_products}
Чтобы удалить нажмите /remove_delivery_category_by_id_{cat['delivery_category_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_category_for_remove_from_stock(category_list):
    """Формируем список локаций для временного снятия с продажи"""
    mes = ''

    for cat in category_list:
        count_products = await db.get_count_products(cat['category_id'])
        category = f"""{cat['category_id']}. {cat['category_name']}
Количество товаров в категории: {count_products}
Чтобы убрать из продажи нажмите /remove_from_stock_category_by_id_{cat['category_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_category_for_return_to_stock(category_list):
    """Формируем список локаций для временного снятия с продажи"""
    mes = ''

    for cat in category_list:
        count_products = await db.get_count_products(cat['category_id'])
        category = f"""{cat['category_id']}. {cat['category_name']}
Количество товаров в категории: {count_products}
Чтобы убрать из продажи нажмите /return_to_stock_category_by_id_{cat['category_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_products_for_remove_from_stock(products):
    """Формируем список продуктов для временного снятия с продажи"""
    mes = ''

    for prod in products:
        category = f"""{prod['product_id']}. {prod['product_name']}
Чтобы убрать из продажи нажмите /remove_item_from_stock_by_id_{prod['product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_delivery_products_for_remove_from_stock(products):
    """Формируем список продуктов для временного снятия с продажи"""
    mes = ''

    for prod in products:
        category = f"""{prod['delivery_product_id']}. {prod['delivery_product_name']}
Чтобы убрать из продажи нажмите /remove_delivery_item_from_stock_by_id_{prod['delivery_product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_products_for_return_to_stock(products):
    """Формируем список продуктов для временного снятия с продажи"""
    mes = ''

    for prod in products:
        category = f"""{prod['product_id']}. {prod['product_name']}
Чтобы вернуть в продажу нажмите /return_item_to_stock_by_id_{prod['product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_delivery_products_for_return_to_stock(products):
    """Формируем список продуктов для временного снятия с продажи"""
    mes = ''

    for prod in products:
        category = f"""{prod['delivery_product_id']}. {prod['delivery_product_name']}
Чтобы вернуть в продажу нажмите /return_delivery_item_to_stock_by_id_{prod['delivery_product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_delivery_products_for_edit(products):
    """Формируем список продуктов для временного снятия с продажи"""
    mes = ''

    for prod in products:
        category = f"""{prod['delivery_product_id']}. {prod['delivery_product_name']}
Чтобы изменить цену нажмите /edit_delivery_item_price_by_id_{prod['delivery_product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_products_for_edit(products):
    """Формируем список продуктов для изменения"""
    mes = ''

    for prod in products:
        category = f"""{prod['product_id']}. {prod['product_name']}
Чтобы изменить нажмите /edit_item_by_id_{prod['product_id']}\n\n"""
        mes += category
    return mes


async def get_list_of_seller_admins(seller_admins_list):
    """Формируем список админов локаций для удаления"""
    mes = ''

    for sa in seller_admins_list:
        if sa['admin_seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['admin_seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        sadmin = f"""{sa['admin_seller_id']}. {sa['admin_seller_name']}
telegramID - {sa['admin_seller_telegram_id']}
Локация: {location_name}
Чтобы удалить нажмите /remove_seller_admin_by_id_{sa['admin_seller_id']}\n\n"""
        mes += sadmin
    return mes


async def get_list_of_seller_admins_for_reset(seller_admins_list):
    """Формируем список админов локаций для сбрасывания локации"""
    mes = ''

    for sa in seller_admins_list:
        if sa['admin_seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['admin_seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        sadmin = f"""{sa['admin_seller_id']}. {sa['admin_seller_name']}
telegramID - {sa['admin_seller_telegram_id']}
Локация: {location_name}
Чтобы открепить от локации нажмите /reset_seller_admin_by_id_{sa['admin_seller_id']}\n\n"""
        mes += sadmin
    return mes


async def get_list_of_seller_admins_for_change(seller_admins_list):
    """Формируем список админов локаций для сбрасывания локации"""
    mes = ''

    for sa in seller_admins_list:
        if sa['admin_seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['admin_seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        sadmin = f"""{sa['admin_seller_id']}. {sa['admin_seller_name']}
telegramID - {sa['admin_seller_telegram_id']}
Локация: {location_name}
Чтобы изменить локацию нажмите /change_seller_admin_location_by_id_{sa['admin_seller_id']}\n\n"""
        mes += sadmin
    return mes


async def get_list_of_sellers(sellers_list):
    """Формируем список продавцов локаций для удаления"""
    mes = ''

    for sa in sellers_list:
        if sa['seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{sa['seller_id']}. {sa['seller_name']}
telegramID - {sa['seller_telegram_id']}
Локация: {location_name}
Чтобы удалить нажмите /remove_seller_by_id_{sa['seller_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_sellers_location(sellers_list):
    """Формируем список продавцов локаций для удаления"""
    mes = ''

    for sa in sellers_list:
        seller = f"""{sa['seller_id']}. {sa['seller_name']}
telegramID - {sa['seller_telegram_id']}
Чтобы удалить нажмите /remove_seller_{sa['seller_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_couriers_location(courier_list):
    """Формируем список курьеров локаций для удаления"""
    mes = ''

    for sa in courier_list:
        seller = f"""{sa['courier_id']}. {sa['courier_name']}
telegramID - {sa['courier_telegram_id']}
Чтобы удалить нажмите /remove_courier_{sa['courier_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_sellers_for_change(seller_admins_list):
    """Формируем список продавцов локаций для удаления"""
    mes = ''

    for sa in seller_admins_list:
        if sa['seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{sa['seller_id']}. {sa['seller_name']}
telegramID - {sa['seller_telegram_id']}
Локация: {location_name}
Чтобы изменить локацию нажмите /change_seller_location_by_id_{sa['seller_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_sellers_for_reset(seller_admins_list):
    """Формируем список продавцов локаций для сбрасывания"""
    mes = ''

    for sa in seller_admins_list:
        if sa['seller_location_id']:
            location_name = await db.get_location_name_by_id(sa['seller_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{sa['seller_id']}. {sa['seller_name']}
telegramID - {sa['seller_telegram_id']}
Локация: {location_name}
Чтобы открепить от локации нажмите /reset_seller_by_id_{sa['seller_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_couriers(couriers_list):
    """Формируем список курьеров для удаления"""
    mes = ''

    for cour in couriers_list:
        if cour['courier_location_id']:
            location_name = await db.get_location_name_by_id(cour['courier_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{cour['courier_id']}. {cour['courier_name']}
telegramID - {cour['courier_telegram_id']}
Локация: {location_name}
Чтобы удалить нажмите /remove_courier_by_id_{cour['courier_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_delivery_couriers(couriers_list):
    """Формируем список курьеров для удаления"""
    mes = ''

    for cour in couriers_list:
        seller = f"""{cour['delivery_courier_id']}. {cour['delivery_courier_name']}
telegramID - {cour['delivery_courier_telegram_id']}
Чтобы удалить нажмите /remove_delivery_courier_by_id_{cour['delivery_courier_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_couriers_for_reset(couriers_list):
    """Формируем список курьеров для сбрасывания"""
    mes = ''

    for cour in couriers_list:
        if cour['courier_location_id']:
            location_name = await db.get_location_name_by_id(cour['courier_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{cour['courier_id']}. {cour['courier_name']}
telegramID - {cour['courier_telegram_id']}
Локация: {location_name}
Чтобы открепить от локации нажмите /reset_courier_by_id_{cour['courier_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_couriers_for_change(couriers_list):
    """Формируем список курьеров для перезакрепления"""
    mes = ''

    for cour in couriers_list:
        if cour['courier_location_id']:
            location_name = await db.get_location_name_by_id(cour['courier_location_id'])
        else:
            location_name = 'Не закреплен за локацией'
        seller = f"""{cour['courier_id']}. {cour['courier_name']}
telegramID - {cour['courier_telegram_id']}
Локация: {location_name}
Чтобы сменить локацию нажмите /change_courier_location_by_id_{cour['courier_id']}\n\n"""
        mes += seller
    return mes


async def get_list_of_products(products_list):
    """Формируем список локаций для удаления"""
    mes = ''

    for prod in products_list:
        product = f"""{prod['product_id']}. {prod['product_name']}
Чтобы удалить нажмите /remove_item_by_id_{prod['product_id']}\n\n"""
        mes += product
    return mes


async def get_list_of_delivery_products(products_list):
    """Формируем список локаций для удаления"""
    mes = ''

    for prod in products_list:
        product = f"""{prod['delivery_product_id']}. {prod['delivery_product_name']}
Чтобы удалить нажмите /remove_delivery_item_by_id_{prod['delivery_product_id']}\n\n"""
        mes += product
    return mes


async def get_sizes(sizes_list):
    """Формируем список размеров"""
    mes = ''
    for size in sizes_list:
        size = f"""Размер: {size['size_name']}
Цены:
    1шт = {size['price_1']} руб
    2шт = {size['price_2']} руб
    3шт = {size['price_3']} руб
    4шт = {size['price_4']} руб
    5шт = {size['price_5']} руб
    6+шт = {size['price_6']} руб\n\n"""
        mes += size
    return mes


async def get_sizes_for_remove(sizes_list):
    """Формируем список размеров"""
    mes = ''
    for size in sizes_list:
        size = f"""\nРазмер: {size['size_name']}
Чтобы удалить введите /remove_size_by_id_{size['size_id']}\n"""
        mes += size
    return mes


async def get_sizes_for_edit(sizes_list):
    """Формируем список размеров"""
    mes = ''
    for size in sizes_list:
        size = f"""\nРазмер: {size['size_name']}
Чтобы изменить введите /edit_size_by_id_{size['size_id']}\n"""
        mes += size
    return mes


async def get_formatted_date(day, delta):
    """Форматируем дату"""
    date = (day + timedelta(days=delta)).strftime("%d.%m.%Y")
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    weekday = (day + timedelta(days=delta)).weekday()
    result = {
        'num': weekday,
        'day': weekdays[weekday],
        'date': date
    }
    return result


async def get_list_of_delivery_orders(orders):
    """Формируем список активных заказов"""
    mes = ''
    for ord in orders:
        order = f"""{blue_diamond_em}Заказ № {ord['delivery_order_id']}. 
{await get_delivery_product_list(ord['delivery_order_id'])}
Сумма заказа: {ord['delivery_order_final_price']} руб.
Дата доставки {ord['delivery_order_day_for_delivery'].strftime("%d.%m.%Y")} {weekdays[ord['delivery_order_day_for_delivery'].weekday()]}
Время доставки {ord['delivery_order_time_info']}
{warning_em} Вы можете изменить дату и время доставки заказа не позднее, чем за 3 часа до доставки.
{warning_em} Отменить заказ можно не позднее, чем за 12 часов до доставки.
{warning_em} Внимание! После изменения даты/времени доставки, заказ отменить будет нельзя.
{attention_em} Чтобы изменить или отменить заказ нажмите /change_delivery_order_by_id_{ord['delivery_order_id']}\n\n"""
        mes += order
    return mes


async def get_delivery_order_info_message(order_data):
    """формируем сообщение"""
    return f"""
Номер заказа: № {order_data['delivery_order_id']}
Адрес доставки: {order_data['location_name']}, 
{order_data['location_address']}
    {await get_delivery_product_list(order_data['delivery_order_id'])}
Стоимость заказа: {order_data['delivery_order_final_price']} руб.
Дата доставки: {order_data['delivery_order_day_for_delivery'].strftime("%d.%m.%Y")} {weekdays[order_data['delivery_order_day_for_delivery'].weekday()]}
Время доставки: {order_data['delivery_order_time_info']}
"""
