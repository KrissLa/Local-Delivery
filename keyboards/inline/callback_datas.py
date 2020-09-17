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

back_to_product_from_sizes_list_data = CallbackData('back_to_product_f', 'category_id')

back_to_size_from_price_list_data = CallbackData('back_to_size', 'product_id')

need_pass_data = CallbackData('need_pass', 'status')

couriers_data = CallbackData('couriers', 'courier_tg_id', 'order_id')

active_order_data = CallbackData('active', 'order_id', 'delivery_method', 'user_id')

active_bonus_order_data = CallbackData('active_bon', 'order_id', 'user_id')

order_is_delivered = CallbackData('order_is_del', 'order_id', 'user_id')

bonus_order_is_delivered_data = CallbackData('bonus_order_is_del', 'order_id', 'user_id')

bonuses_data = CallbackData('bonus', 'count_bonus')

confirm_bonus_order = CallbackData('confirm_bonus', 'b_order_id')

cancel_bonus_order_data = CallbackData('cancel_bonus', 'b_order_id', 'quantity')


admin_data = CallbackData('delete_admin', 'admin_id')

metro_del_data = CallbackData('delete_metro', 'metro_id')

location_data = CallbackData('loc_for_l_o', 'location_id')


new_item_size = CallbackData('with_size', 'status')


edit_item_data = CallbackData('edit_item', 'item_id', 'subject')


edit_item_sizes_data = CallbackData('edit_item_sizes', 'item_id', 'subject')

edit_size_data = CallbackData('edit_size', 'size_id', 'subject')
