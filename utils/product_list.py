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