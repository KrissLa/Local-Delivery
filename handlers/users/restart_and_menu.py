from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.menu import menu_keyboard
from loader import dp


# @dp.message_handler(text=['Меню', 'Акции и бонусы', 'Профиль', 'О сервисе'],
#                     state=[ProfileState.WaitAddress,
#                            Menu.WaitAddress])
# async def restart(message: types.Message):
#     """restart"""
#     await message.answer('Если Вы не хотите прерывать заказ, просто продолжите его выше.'
#                          ' Если хотите прервать заказ, нажмите на кнопку.',
#                          reply_markup=InlineKeyboardMarkup(
#                              inline_keyboard=[
#                                  [
#                                      InlineKeyboardButton(
#                                          text='Да, прервать заказ.',
#                                          callback_data='cancel_order_menu'
#                                      )
#                                  ]
#                              ]
#                          ))





# @dp.message_handler(state=[Menu.WaitTime, Menu.WaitCategory, Menu.WaitProduct,
#                            Menu.WaitProductSize,
#                            Menu.WaitProductSizeBack,
#                            Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
#                            Menu.WaitUserConfirmationPickup, Menu.WaitPass,
#                            ])
# async def restart(message: types.Message):
#     """restart"""
#     await message.answer('Если Вы не хотите прерывать заказ, просто продолжите его выше.'
#                          ' Если хотите прервать заказ, нажмите на кнопку.',
#                          reply_markup=InlineKeyboardMarkup(
#                              inline_keyboard=[
#                                  [
#                                      InlineKeyboardButton(
#                                          text='Да, прервать заказ.',
#                                          callback_data='cancel_order_menu'
#                                      )
#                                  ]
#                              ]
#                          ))


@dp.message_handler(commands=['restart'], state=['*'])
async def restart(message: types.Message, state: FSMContext):
    """restart"""
    await state.finish()
    await message.answer('Перезагружен',
                         reply_markup=menu_keyboard)
