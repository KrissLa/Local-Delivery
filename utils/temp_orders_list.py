async def get_temp_orders_list_message(orders):
    """Формируем список покупок за сеанс"""
    mes = ''
    num = 1
    for order in orders:
        mes += f'   {num}. {order["product_name"]} - {order["quantity"]} шт\n'
        num += 1
    return mes


async def get_final_price(orders):
    """Считаем окончательную цену"""
    fin_price = 0
    for order in orders:
        fin_price += order['order_price']
    return int(fin_price)


async def get_couriers_list(couriers):
    """Формируем список курьеров"""
    mes = ''
    num = 1
    for cour in couriers:
        mes += f"   {num}. {cour['courier_name']}\n"
        num += 1
    return mes
