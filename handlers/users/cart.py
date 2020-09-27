from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import remove_from_cart_data
from keyboards.inline.inline_keyboards import cart_markup
from loader import dp, db
from states.menu_states import Menu
from utils.emoji import attention_em
from utils.send_messages import send_cart
from utils.temp_orders_list import get_temp_orders_list_message, get_final_price


@dp.callback_query_handler(remove_from_cart_data.filter(), state=Menu.OneMoreOrNext)
async def remove_item_from_cart(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Убираем товары из корзины"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await db.delete_temp_order_by_id(order_id)
    temp_orders = await db.get_temp_orders(call.from_user.id)
    final_price = await get_final_price(temp_orders)
    list_products = await get_temp_orders_list_message(temp_orders)
    await state.update_data(list_products=list_products)
    await state.update_data(final_price=final_price)
    await call.answer('Готово')



@dp.message_handler(commands=['cart'], state='*')
async def cart(message: types.Message, state: FSMContext):
    """Корзина"""
    await state.finish()
    temp_orders = await db.get_temp_orders(message.from_user.id)
    if temp_orders:
        list_products = await get_temp_orders_list_message(temp_orders)
        final_price = await get_final_price(temp_orders)
        await state.update_data(list_products=list_products)
        await state.update_data(final_price=final_price)
        await send_cart(temp_orders, message.from_user.id)
        await message.answer(f'Сумма заказа - {final_price} руб.\n'
                             'Оформить заказ\n'
                             f'{attention_em} Доставка работает в будни с 11 до 17',
                             reply_markup=cart_markup)
        await Menu.OneMoreOrNext.set()
    else:
        await message.answer('Ваша корзина пуста')


@dp.message_handler(commands=['clear_cart'], state=['*'])
async def cart(message: types.Message, state: FSMContext):
    """Корзина"""
    await state.finish()
    await db.clear_cart(message.from_user.id)
    await db.clear_empty_orders(message.from_user.id)
    await message.answer('Корзина очищена.\n'
                         'Вы в главном меню',
                         reply_markup=menu_keyboard)


@dp.message_handler(commands=['menu'], state=['*'])
async def menu(message: types.Message):
    """Отправляем меню"""
    await message.answer('Отправляю меню',
                         reply_markup=menu_keyboard)



@dp.message_handler(commands=['order_status'], state=['*'])
async def get_order_status(message: types.Message):
    """Статус заказа"""
    orders = await db.get_orders_for_user(message.from_user.id)
    if orders:
        for order in orders:
            if order['delivery_method'] == 'С доставкой':
                if order['deliver_to']:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{order['order_info']}"
                                         f"Стоимость: {order['order_price']}\n"
                                         f"Будет доставлен в {order['deliver_to'].strftime('%H:%M')}\n"
                                         f"Статус заказа - {order['order_status']}\n\n")
                else:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{order['order_info']}\n"
                                         f"Стоимость: {order['order_price']}\n"
                                         f"Статус заказа - {order['order_status']}\n\n")
            else:
                if order['deliver_to']:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{order['order_info']}"
                                         f"Стоимость: {order['order_price']}\n"
                                         f"Будет готов в {order['deliver_to'].strftime('%H:%M')}\n"
                                         f"Статус заказа - {order['order_status']}\n\n")
                else:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{order['order_info']}"
                                         f"Стоимость: {order['order_price']}\n"
                                         f"Статус заказа - {order['order_status']}\n\n")
    else:
        await message.answer('Нет активных заказов')
