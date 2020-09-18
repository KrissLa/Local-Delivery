from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp

from keyboards.default.menu import menu_keyboard
from loader import dp
from states.bonus_state import Bonus
from states.menu_states import Menu


@dp.message_handler(text="О сервисе", state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                                                 Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                                                 Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                                                 Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                                                 Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                                                 Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                                                 Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                                                 Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                                                 ])
@dp.message_handler(text="Акции и бонусы", state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                                                 Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                                                 Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                                                 Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                                                 Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                                                 Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                                                 Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                                                 Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                                                 ])
@dp.message_handler(text="Профиль", state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                                                 Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                                                 Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                                                 Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                                                 Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                                                 Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                                                 Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                                                 Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                                                 ])
@dp.message_handler(text="Меню", state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                                                 Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                                                 Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                                                 Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                                                 Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                                                 Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                                                 Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                                                 Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                                                 ])
@dp.message_handler(CommandHelp(), state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                                                 Menu.WaitQuantity, Menu.WaitQuantityBack, Menu.WaitProductSize,
                                                 Menu.WaitProductSizeBack, Menu.WaitQuantityBackWithSize,
                                                 Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                                                 Menu.WaitUserConfirmationPickup, Bonus.Count, Bonus.WaitSeller,
                                                 Menu.WaitQuantityBackWithSizeId, Menu.WaitQuantity6,
                                                 Menu.WaitQuantity6Back, Menu.WaitQuantity6BackWithSize,
                                                 Menu.WaitQuantity6BackWithSizeId, Menu.WaitPass,
                                                 ])
@dp.message_handler(commands=['restart'], state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
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
    await message.answer('Сначала завершите или отмените заказ')


@dp.message_handler(commands=['restart'], state=['*'])
async def restart(message: types.Message, state: FSMContext):
    """restart"""
    await state.finish()
    await message.answer('Перезагружен',
                         reply_markup=menu_keyboard)
