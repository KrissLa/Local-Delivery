from aiogram.utils.callback_data import CallbackData

metro_data = CallbackData('set_metro', 'metro_id')

local_object_data = CallbackData('set_local_object', 'local_object_id')

categories_data = CallbackData('set_category', 'category_id')


delivery_categories_data = CallbackData('deliv_category', 'category_id')

product_list_data = CallbackData('set_product', 'product_id')

delivery_product_data = CallbackData('deliv_product', 'product_id', 'price')

product_count_price_data = CallbackData('product_quantity', 'quantity', 'price')

delivery_product_count_data = CallbackData('deliv_quantity', 'quantity', 'price')

deliver_to_time_data = CallbackData('deliver_ro', 'time', 'value', 'del_type')

confirm_order_seller_data = CallbackData('confirm_order_seller', 'order_id', 'status', 'delivery_method')

size_product_data = CallbackData('size_product', 'size_id', 'product_id')

size_data = CallbackData('edit_size_price', 'size_id')

back_to_product_list_data = CallbackData('back_to_product', 'category_id')

back_to_product_from_sizes_list_data = CallbackData('back_to_product_f', 'category_id')

back_to_size_from_price_list_data = CallbackData('back_to_size', 'product_id')

need_pass_data = CallbackData('need_pass', 'status')

couriers_data = CallbackData('couriers', 'courier_tg_id', 'order_id')

delivery_couriers_data = CallbackData('delivery_cour', 'delivery_courier_id', 'delivery_courier_telegram_id', 'order_id')

cancel_courier_data = CallbackData('cancel_courier', 'order_id')

active_order_data = CallbackData('active', 'order_id', 'delivery_method', 'user_id')

active_order_cancel_data = CallbackData('active_cancel', 'order_id')

active_bonus_order_data = CallbackData('active_bon', 'order_id', 'user_id')

order_is_delivered = CallbackData('order_is_del', 'order_id', 'user_id')

bonus_order_is_delivered_data = CallbackData('bonus_order_is_del', 'order_id', 'user_id')

bonuses_data = CallbackData('bonus', 'count_bonus')

confirm_bonus_order = CallbackData('confirm_bonus', 'b_order_id')

cancel_bonus_order_data = CallbackData('cancel_bonus', 'b_order_id', 'quantity')

cancel_bonus_order_data_sellers = CallbackData('cancel_bonus', 'b_order_id', 'quantity')

admin_data = CallbackData('delete_admin', 'admin_id')

metro_del_data = CallbackData('delete_metro', 'metro_id')

location_data = CallbackData('loc_for_l_o', 'location_id')


new_item_size = CallbackData('with_size', 'status')


edit_item_data = CallbackData('edit_item', 'item_id', 'subject')


edit_item_sizes_data = CallbackData('edit_item_sizes', 'item_id', 'subject')

edit_size_data = CallbackData('edit_size', 'size_id', 'subject')

page_call_data = CallbackData('next', 'page')

back_data = CallbackData('back', 'page')

remove_from_cart_data = CallbackData('remove_fc', 'order_id')

cancel_order_data = CallbackData('cancel_order', 'order_id')

delivery_date_data = CallbackData('date_data', 'date', 'weekday')

delivery_time_data = CallbackData('time_data', 'time', "choice")

take_delivery_order = CallbackData('take', 'order_id')

confirm_delivery_order = CallbackData('confirm', 'order_id')

dont_take_delivery_order = CallbackData('dont_take', 'order_id')

reviev_order_data = CallbackData('review', 'order_id')

reviev_bonus_order_data = CallbackData('bonus_review', 'order_id')

statistics_date_data = CallbackData('st_date', 'period')

statistics_date_delivery = CallbackData('st_date_del', 'period')

statistics_date_location_delivery = CallbackData('st_date_loc_del', 'period', 'location_id', 'admin')

admin_statistics_date_data_all = CallbackData('st_admin_date', 'period')

statistics_year_data = CallbackData('year_data', 'year')

statistics_year_location_data = CallbackData('year_data_loc', 'year', 'location_id', 'admin')

statistics_delivery_year_data = CallbackData('year_data_del', 'year')

statistics_year_month_data = CallbackData('year_month', 'year', 'month')

statistics_delivery_year_month_data = CallbackData('year_month_del', 'year', 'month')

statistics_delivery_year_month_loc_data = CallbackData('y_m_d_loc', 'year', 'month', 'location_id', 'admin')

statistics_day_data = CallbackData('day_data', 'day', 'month', 'year')

statistics_delivery_day_data = CallbackData('day_del_data', 'day', 'month', 'year')

statistics_delivery_day_loc_data = CallbackData('day_del_data', 'day', 'month', 'year', 'location_id', 'admin')

courier_confirm_data = CallbackData('del_cour', 'status', 'courier_id', 'order_id')

courier_confirm_changes = CallbackData('del_cour_changes', 'status', 'courier_id', 'order_id')

statistics_location_data = CallbackData('st_location', "location_id")


statistics_location_data_del = CallbackData('st_location_del', "location_id")


