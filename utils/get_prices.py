def get_price_list(product):
    """Получаем список цен в одном виде"""
    try:
        prices = {
            'price_1': product['price_1'],
            'price_2': product['price_2'],
            'price_3': product['price_3'],
            'price_4': product['price_4'],
            'price_5': product['price_5'],
            'price_6': product['price_6'],
        }
    except Exception:
        prices = {
            'price_1': product['local_price_1'],
            'price_2': product['local_price_2'],
            'price_3': product['local_price_3'],
            'price_4': product['local_price_4'],
            'price_5': product['local_price_5'],
            'price_6': product['local_price_6'],
        }
    return prices
