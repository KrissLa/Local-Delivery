from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default.menu import menu_keyboard
from loader import dp, db


@dp.callback_query_handler(text='cancel_order', state=['*'])
async def cancel_order(call: CallbackQuery, state: FSMContext):
    """Отмена заказа, очистка корзины"""
    await call.message.edit_reply_markup()
    await state.finish()
    await db.clear_cart(call.from_user.id)
    await db.clear_empty_orders(call.from_user.id)
    await call.answer("Вы отменили заказ. Корзина товаров очищена")
    await call.message.answer('Вы в главном меню',
                              reply_markup=menu_keyboard)
