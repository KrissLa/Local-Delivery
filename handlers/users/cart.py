from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import remove_from_cart_data, cancel_order_data
from keyboards.inline.inline_keyboards import cancel_order_user_markup, \
    back_markup
from loader import dp, db
from states.menu_states import Menu
from utils.emoji import warning_em, error_em
from utils.temp_orders_list import get_temp_orders_list_message, get_final_price


@dp.callback_query_handler(cancel_order_data.filter(), state=[Menu.OrderStatus,
                                                              Menu.WaitReasonUser])
async def cancel_order(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Отмена заказа"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    if await db.can_cancel(order_id):
        await state.update_data(canceled_order_id=order_id)
        await call.message.answer('Вы действительно хотите отменить заказ?',
                                  reply_markup=cancel_order_user_markup)
        if await state.get_state() == 'Menu:WaitReasonUser':
            await Menu.OrderStatus.set()
    else:
        await call.message.answer(f'{error_em} Извините, но на этой стадии заказ отменить нельзя')


@dp.callback_query_handler(text='back', state=[Menu.OrderStatus,
                                               Menu.WaitReasonUser])
async def back(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer('Вы в главном меню. Заказ не отменен',
                              reply_markup=menu_keyboard)


@dp.callback_query_handler(text='cancel_order_by_user', state=Menu.OrderStatus)
async def confirm_cancelling_order(call: CallbackQuery):
    """Подтверждение отмены"""
    await call.message.edit_reply_markup()
    await call.message.answer(f'{warning_em} Для завершения отмены заказа, пожалуйста, напишите причину отмены одним '
                              f'сообщением.',
                              reply_markup=back_markup)
    await Menu.WaitReasonUser.set()


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
