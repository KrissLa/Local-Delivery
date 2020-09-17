from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import confirm_order_seller_data, confirm_bonus_order
from loader import bot


async def send_message_to_sellers_bonus(sellers_list, order_info):
    """Отправляем сообщение продавцам"""
    message = f"""Новый бонусный заказ № {order_info['bonus_order_id']}!
Количество бонусных роллов: {order_info['bonus_quantity']}
Пожалуйста, подойдите к кассе и, после выбора роллов клиентом, подтвердите заказ"""
    for seller in sellers_list:
        await bot.send_message(seller['seller_telegram_id'],
                               message,
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(
                                               text=f'Подтвердить бонусный заказ № {order_info["bonus_order_id"]}',
                                               callback_data=confirm_bonus_order.new(
                                                   b_order_id=order_info["bonus_order_id"])
                                           )
                                       ]

                                   ]
                               )
                               )


async def send_message_to_sellers(sellers_list, order_detail):
    """Отправляем сообщение продавцам"""
    if order_detail['delivery_method'] == "С доставкой":
        message = f"""Новый заказ № {order_detail['order_id']}
{order_detail['order_info']}
Тип доставки: {order_detail['delivery_method']}
Адрес доставки: {order_detail["order_local_object_name"]},
{order_detail["delivery_address"]}
Доставить через {order_detail["time_for_delivery"]} минут
Пропуск для курьеров: {order_detail["order_pass_for_courier"]}
Цена заказа: {order_detail["order_price"]} руб.
Статус заказа: {order_detail["order_status"]}"""
    else:
        message = f"""
Новый заказ № {order_detail['order_id']}
{order_detail['order_info']}
Тип доставки: {order_detail['delivery_method']}
{order_detail["delivery_address"]}
Приготовить через {order_detail["time_for_delivery"]} минут
Цена заказа: {order_detail["order_price"]} руб.
Статус заказа: {order_detail["order_status"]}"""

    for seller in sellers_list:
        await bot.send_message(seller['seller_telegram_id'],
                               message,
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(
                                               text=f'Принять заказ № {order_detail["order_id"]}',
                                               callback_data=confirm_order_seller_data.new(
                                                   order_id=order_detail["order_id"],
                                                   status='confirm',
                                                   delivery_method=order_detail['delivery_method'])
                                           )
                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text=f'Отклонить заказ № {order_detail["order_id"]}',
                                               callback_data=confirm_order_seller_data.new(
                                                   order_id=order_detail["order_id"],
                                                   status='cancel',
                                                   delivery_method=order_detail['delivery_method'])
                                           )
                                       ]

                                   ]
                               )
                               )


async def send_confirm_message_to_user_pickup(user_id, order_id, time):
    """Отправляем сообщение пользователю"""
    await bot.send_message(chat_id=user_id,
                           text=f'Ваш заказ № {order_id} подтвержден и будет готов к {time}\n'
                                f"Вы получите уведомление о готовности заказа.")


async def send_message_to_courier_order(courier_id, order_info):
    """Отправка сообщения о назначении заказа курьеру"""
    await bot.send_message(chat_id=courier_id,
                           text=f'Вам назначен заказ № {order_info["order_id"]}\n'
                                f'{order_info["order_info"]}\n'
                                f'Доставить по адресу:\n'
                                f'{order_info["order_local_object_name"]}, {order_info["delivery_address"]}\n'
                                f'до {order_info["deliver_to"].strftime("%H:%M")}\n'
                                f'Стоимость заказа: {order_info["order_price"]} руб\n'
                                f'Когда заказ будет готов, Вам придет уведомление')


async def send_confirm_message_to_user_delivery(order_info, courier_name):
    """Отправляем сообщение пользователю о том, что заказ подтвержден"""
    await bot.send_message(chat_id=order_info["order_user_telegram_id"],
                           text=f'Ваш заказ № {order_info["order_id"]} подтвержден и будет доставлен к '
                                f'{order_info["deliver_to"].strftime("%H:%M")}\n'
                                f'Ваш курьер: {courier_name}\n'
                                f"Вы можете увидеть статус заказа командой /order_status")