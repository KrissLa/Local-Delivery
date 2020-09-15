from aiogram.utils.callback_data import CallbackData

metro_data = CallbackData('set_metro', 'metro_id')

local_object_data = CallbackData('set_local_object', 'local_object_id')

categories_data = CallbackData('set_category', 'category_id')

product_list_data = CallbackData('set_product', 'product_id')

product_count_price_data = CallbackData('product_quantity', 'quantity', 'price')

deliver_to_time_data = CallbackData('deliver_ro', 'time', 'value', 'del_type')

confirm_order_seller_data = CallbackData('confirm_order_seller', 'order_id', 'status', 'delivery_method')

size_product_data = CallbackData('size_product', 'size_id', 'product_id')

back_to_product_list_data = CallbackData('back_to_product', 'category_id')

back_to_product_from_sizes_list_data = CallbackData('back_to_product', 'category_id')

back_to_size_from_price_list_data = CallbackData('back_to_size', 'product_id')

need_pass_data = CallbackData('need_pass', 'status')

couriers_data = CallbackData('couriers', 'courier_tg_id', 'order_id')

active_order_data = CallbackData('active', 'order_id', 'delivery_method', 'user_id')

order_is_delivered = CallbackData('order_is_del', 'order_id', 'user_id')
