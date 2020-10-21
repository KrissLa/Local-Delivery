import logging
import random
from datetime import datetime, timedelta

from loader import db

del_time = [10, 15, 20, 25, 40, 60]


def get_date_list():
    date_list = []
    start_date = datetime(2018, 3, 21, 4, 25, 2)
    for i in range(10000):
        hour = random.randint(1, 5)
        min = random.randint(1, 59)
        start_date = start_date + timedelta(hours=hour, minutes=min)
        date_list.append(start_date)
    print(date_list)
    return date_list


async def get_del_tr():
    del_time = [10, 15, 20, 25, 40, 60]
    return random.choice(del_time)


def get_del_time(date, time):
    return date + timedelta(minutes=time)


async def get_user_id():
    user_id = random.choice(await db.test_users())['user_id']
    return user_id


async def get_local():
    local_id = random.choice(await db.test_local())

    return local_id["local_object_id"]


async def get_seller(local_id):
    logging.info(local_id)
    seller_id = random.choice(await db.test_sellers(local_id))
    return seller_id['seller_id']


async def get_courier(local_id):
    courier_id = random.choice(await db.test_courier(local_id))
    return courier_id["courier_id"]


async def get_accepted_time(date):
    acc_minutes = random.randint(1, 20)
    acc_seconds = random.randint(1, 59)
    return date + timedelta(minutes=acc_minutes, seconds=acc_seconds)


async def get_cancel_time(date):
    acc_minutes = random.randint(1, 27)
    acc_seconds = random.randint(1, 59)
    return date + timedelta(minutes=acc_minutes, seconds=acc_seconds)


async def get_delivery_at(date):
    acc_minutes = random.randint(1, 5)
    acc_seconds = random.randint(1, 59)
    date1 = date - timedelta(minutes=acc_minutes, seconds=acc_seconds)
    date2 = date + timedelta(minutes=acc_minutes, seconds=acc_seconds)
    return random.choice([date1, date2])


async def get_dil_method():
    return random.choice(['Доставка', 'Самовывоз'])


async def get_status():
    return random.choice(['Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером', 'Выполнен', 'Выполнен',
                          'Выполнен', 'Выполнен', 'Выполнен'])


async def get_review():
    return random.choice(['Все круто', '', '', 'Все плохо', '', 'все понравилось, спасибо', '', '', '', '',
                          'Больше НИКОГДА не буду заказывать у вас еду'])


async def get_reason():
    return random.choice(['Не успел', 'Просто так', 'Еда остыла', 'Я передумал',
                          'Курьер сломался'])


async def get_quant():
    return random.randint(1, 5)


async def get_products(quant):
    return await db.test_products(quant)


async def get_prod_quant():
    return random.randint(1, 6)


async def get_price(products, quant):
    sum = 0
    for pr in products:
        if quant == 1:
            sum += pr['price_1']
        elif quant == 2:
            sum += pr['price_2'] * 2
        elif quant == 3:
            sum += pr['price_3'] * 3
        elif quant == 4:
            sum += pr['price_4'] * 4
        elif quant == 5:
            sum += pr['price_5'] * 5
        elif quant == 6:
            sum += pr['price_6'] * 6
    return sum


async def test_op(op_order_id, op_product_id, op_product_name, op_quantity,
                  op_price_per_unit, op_price):
    await db.test_order_product(op_order_id, op_product_id, op_product_name, op_quantity,
                                op_price_per_unit, op_price)


async def generate_table():
    date_list = get_date_list()
    n = 1
    for date in date_list:
        order_user_id = await get_user_id()
        order_local_object_id = await get_local()
        order_seller_id = await get_seller(order_local_object_id)
        order_delivery_method = await get_dil_method()
        if order_delivery_method == 'Доставка':
            order_courier_id = await get_courier(order_local_object_id)
        order_date = date
        order_created_at = date
        order_accepted_at = await get_accepted_time(date)
        order_status = await get_status()
        order_deliver_through = await get_del_tr()
        order_time_for_delivery = get_del_time(date, order_deliver_through)
        if order_status in ['Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером']:
            order_canceled_at = await get_cancel_time(order_accepted_at)
            order_reason_for_rejection = await get_reason()
        else:
            order_delivered_at = await get_delivery_at(order_time_for_delivery)

        order_review = await get_review()
        if order_delivery_method == 'Доставка':
            if order_status in ['Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером']:
                await db.test_order(order_year=int(order_date.strftime("%Y")),
                                    order_month=int(order_date.strftime("%m")),
                                    order_user_id=order_user_id,
                                    order_seller_id=order_seller_id,
                                    order_date=order_date,
                                    order_created_at=order_created_at,
                                    order_accepted_at=order_accepted_at,
                                    order_time_for_delivery=order_time_for_delivery,
                                    order_deliver_through=order_deliver_through,
                                    order_local_object_id=order_local_object_id,
                                    order_delivery_method=order_delivery_method,
                                    order_status=order_status,
                                    order_canceled_at=order_canceled_at,
                                    order_review=order_review,
                                    order_reason_for_rejection=order_reason_for_rejection,
                                    order_courier_id=order_courier_id)
            else:
                await db.test_order(order_year=int(order_date.strftime("%Y")),
                                    order_month=int(order_date.strftime("%m")),
                                    order_user_id=order_user_id,
                                    order_seller_id=order_seller_id,
                                    order_date=order_date,
                                    order_created_at=order_created_at,
                                    order_accepted_at=order_accepted_at,
                                    order_time_for_delivery=order_time_for_delivery,
                                    order_deliver_through=order_deliver_through,
                                    order_local_object_id=order_local_object_id,
                                    order_delivery_method=order_delivery_method,
                                    order_status=order_status,
                                    order_delivered_at=order_delivered_at,
                                    order_review=order_review,
                                    order_courier_id=order_courier_id)
        else:
            if order_status in ['Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером']:
                await db.test_order(order_year=int(order_date.strftime("%Y")),
                                    order_month=int(order_date.strftime("%m")),
                                    order_user_id=order_user_id,
                                    order_seller_id=order_seller_id,
                                    order_date=order_date,
                                    order_created_at=order_created_at,
                                    order_accepted_at=order_accepted_at,
                                    order_time_for_delivery=order_time_for_delivery,
                                    order_deliver_through=order_deliver_through,
                                    order_local_object_id=order_local_object_id,
                                    order_delivery_method=order_delivery_method,
                                    order_status=order_status,
                                    order_canceled_at=order_canceled_at,
                                    order_reason_for_rejection=order_reason_for_rejection,
                                    order_review=order_review)
            else:
                await db.test_order(order_year=int(order_date.strftime("%Y")),
                                    order_month=int(order_date.strftime("%m")),
                                    order_user_id=order_user_id,
                                    order_seller_id=order_seller_id,
                                    order_date=order_date,
                                    order_created_at=order_created_at,
                                    order_accepted_at=order_accepted_at,
                                    order_time_for_delivery=order_time_for_delivery,
                                    order_deliver_through=order_deliver_through,
                                    order_local_object_id=order_local_object_id,
                                    order_delivery_method=order_delivery_method,
                                    order_status=order_status,
                                    order_delivered_at=order_delivered_at,
                                    order_review=order_review)

        order_id = await db.test_last_order()

        quant_products = await get_quant()
        products = await get_products(quant_products)
        sum = 0
        for pr in products:
            pr_quant = await get_prod_quant()
            if pr_quant == 1:
                op_price_per_unit = pr['price_1']
            elif pr_quant == 2:
                op_price_per_unit = pr['price_2']
            elif pr_quant == 3:
                op_price_per_unit = pr['price_3']
            elif pr_quant == 4:
                op_price_per_unit = pr['price_4']
            elif pr_quant == 5:
                op_price_per_unit = pr['price_5']
            else:
                op_price_per_unit = pr['price_6']
            op_price = op_price_per_unit * pr_quant
            sum += op_price

            await db.test_order_product(order_id, pr["product_id"], pr['product_name'], pr_quant,
                                        op_price_per_unit, op_price)
        await db.test_price(order_id, sum)
        print(f'Добавил заказ {n}')
        n += 1
