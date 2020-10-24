from loader import db


async def get_product_list(order_id):
    """Формируем список товаров"""
    list_of_products = []
    n = 0
    for pr in await db.get_order_products(order_id):
        n += 1
        list_of_products.append(
            f"  {n}. {pr['op_product_name']}  - {pr['op_quantity']} шт. - {pr['op_price']} руб. ({pr['op_price_per_unit']} руб за ед.)")

    order_products = '\n'.join(list_of_products)
    return order_products


async def get_delivery_product_list(order_id):
    """Формируем список покупок за сеанс"""
    mes = ''
    num = 1
    orders = await db.get_delivery_order_products(order_id)
    for order in orders:
        items = order["dop_quantity"] * 12
        digit = int(str(order["dop_quantity"])[-1])
        if digit == 1 and order["dop_quantity"] != 11:
            tray = 'лоток'
        elif digit in [2, 3, 4] and order["dop_quantity"] not in [12, 13, 14]:
            tray = 'лотка'
        else:
            tray = 'лотков'
        mes += f'   {num}. {order["dop_product_name"]} -\n    {order["dop_quantity"]} ' \
               f'{tray} ({items} шт.) {order["dop_price"]} руб.\n\n'
        num += 1
    return mes