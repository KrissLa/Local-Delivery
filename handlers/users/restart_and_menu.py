from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.menu import menu_keyboard
from loader import dp
from states.bonus_state import Bonus
from states.menu_states import Menu


@dp.message_handler(state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                           Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                           Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                           Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                           Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                           Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                           Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                           Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                           ])
async def restart(message: types.Message):
    """restart"""
    await message.answer('Если Вы не хотите прерывать заказ, просто продолжите его выше.'
                         ' Если хотите прервать заказ, нажмите на кнопку.',
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Да, прервать заказ.',
                                         callback_data='cancel_order_menu'
                                     )
                                 ]
                             ]
                         ))


@dp.message_handler(commands=['restart'], state=['*'])
async def restart(message: types.Message, state: FSMContext):
    """restart"""
    await state.finish()
    await message.answer('Перезагружен',
                         reply_markup=menu_keyboard)
