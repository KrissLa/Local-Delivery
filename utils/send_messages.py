import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import confirm_order_seller_data, confirm_bonus_order, remove_from_cart_data
from loader import bot
from utils.emoji import success_em, attention_em
from utils.product_list import get_product_list


async def send_cart(orders, user_id):
    """Отправяем корзину"""
    num = 1
    for order in orders:
        await bot.send_message(user_id, f'{num}. {order["product_name"]} - {order["quantity"]} шт. '
                                        f'{order["order_price"]} руб.\n',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [
                                       InlineKeyboardButton(
                                           text=f'Убрать из корзины товар {num}',
                                           callback_data=remove_from_cart_data.new(order_id=order['temp_order_id'])
                                       )
                                   ]
                               ]))
        num += 1


async def send_delivery_cart(orders, user_id):
    """Отправяем корзину"""
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

        await bot.send_message(user_id, f'{num}. {order["delivery_product_name"]} -\n{order["delivery_quantity"]} '
                                        f'{tray} ({items} шт.) {order["delivery_order_price"]} руб.\n',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [
                                       InlineKeyboardButton(
                                           text=f'Убрать товар {num}',
                                           callback_data=remove_from_cart_data.new(
                                               order_id=order['temp_delivery_order_id'])
                                       )
                                   ]
                               ]))
        num += 1


async def send_message_to_sellers_bonus(sellers_list, order_info):
    """Отправляем сообщение продавцам"""
    message = f"""Новый бонусный заказ № {order_info['bonus_order_id']}!
Количество бонусных роллов: {order_info['bonus_quantity']}
Пожалуйста, подойдите к кассе и, после выбора роллов клиентом, подтвердите заказ"""
    for seller in sellers_list:
        try:
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
        except Exception as err:
            logging.error(err)


async def send_message_to_sellers(sellers_list, order_detail):
    """Отправляем сообщение продавцам"""
    if order_detail['order_delivery_method'] == "Доставка":
        message = f"""Новый заказ № {order_detail['order_id']}
{await get_product_list(order_detail['order_id'])}
Тип доставки: {order_detail['order_delivery_method']}
Адрес доставки: {order_detail["local_object_name"]},
{order_detail["order_address"]}
Доставить через {order_detail["order_deliver_through"]} минут
Пропуск для курьеров: {order_detail["order_pass_to_courier"]}
Стоимость заказа: {order_detail["order_final_price"]} руб.
Статус заказа: {order_detail["order_status"]}"""
    else:
        message = f"""
Новый заказ № {order_detail['order_id']}
{await get_product_list(order_detail['order_id'])}
Тип доставки: {order_detail['order_delivery_method']}
Адрес самовывоза: {order_detail["order_address"]}
Приготовить через {order_detail["order_deliver_through"]} минут
Стоимость заказа: {order_detail["order_final_price"]} руб.
Статус заказа: {order_detail["order_status"]}"""

    for seller in sellers_list:
        try:
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
                                                       delivery_method=order_detail['order_delivery_method'])
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text=f'Отклонить заказ № {order_detail["order_id"]}',
                                                   callback_data=confirm_order_seller_data.new(
                                                       order_id=order_detail["order_id"],
                                                       status='cancel',
                                                       delivery_method=order_detail['order_delivery_method'])
                                               )
                                           ]

                                       ]
                                   )
                                   )
        except Exception as err:
            logging.error(err)


async def send_confirm_message_to_user_pickup(user_id, order_id, time):
    """Отправляем сообщение пользователю"""
    try:
        await bot.send_message(chat_id=user_id,
                               text=f'{success_em} Ваш заказ № {order_id} подтвержден и будет готов к {time}\n'
                                    f"Вы получите уведомление о готовности заказа.")
    except Exception as err:
        logging.error(err)


async def send_message_to_courier_order(order_id, courier_id, order_info):
    """Отправка сообщения о назначении заказа курьеру"""

    try:
        await bot.send_message(chat_id=courier_id,
                               text=f'Вам назначен заказ № {order_id}\n'
                                    f'{await get_product_list(order_id)}\n'
                                    f'Доставить по адресу: {order_info["local_object_name"]},\n'
                                    f'{order_info["order_address"]}\n'
                                    f'Доставить к: {order_info["order_time_for_delivery"].strftime("%H:%M")}\n'
                                    f'Стоимость заказа: {order_info["order_final_price"]} руб\n'
                                    f'{attention_em} Когда заказ будет готов, Вам придет уведомление')
        return True
    except Exception as err:
        logging.error(err)
        return False


async def send_confirm_message_to_user_delivery(order_id, order_info, courier_name):
    """Отправляем сообщение пользователю о том, что заказ подтвержден"""
    await bot.send_message(chat_id=order_info["user_telegram_id"],
                           text=f'{success_em} Ваш заказ № {order_id} подтвержден и будет доставлен к '
                                f'{order_info["order_time_for_delivery"].strftime("%H:%M")}\n'
                                f'Ваш курьер: {courier_name}\n'
                                f"{attention_em} Вы можете увидеть статус заказа командой /order_status")
