from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsBanned
from keyboards.default.menu import menu_keyboard
from loader import dp, db
from utils.misc import rate_limit


@rate_limit(25, 'help')
@dp.message_handler(IsBanned(), state=['*'])
async def ban(message: types.Message):
    """Ответ забаненым"""
    reason = await db.get_reason_for_ban(message.from_user.id)
    await message.answer(f'Вы забанены\n'
                         f'Причина: {reason}')


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


@dp.callback_query_handler(text='cancel_order_menu', state=['*'])
async def cancel_order_menu(call: CallbackQuery, state: FSMContext):
    """cancel_order_menu"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Вы в главном меню',
                              reply_markup=menu_keyboard)


@dp.callback_query_handler(text='cancel_admin', state=['*'])
async def cancel_admin(call: CallbackQuery, state: FSMContext):
    """cancel_admin"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Операция прервана\n'
                              'Вы в главном меню',
                              reply_markup=menu_keyboard)


@dp.message_handler(commands=['restart'], state=['*'])
async def restart(message: types.Message, state: FSMContext):
    """restart"""
    await state.finish()
    await message.answer('Перезагружен',
                         reply_markup=menu_keyboard)


# @dp.callback_query_handler(cancel_order_data.filter())
# async def confirm_cancel_order(call: CallbackQuery, callback_data: dict):
#     """Получаем подтверждение на отмену зкакза"""

