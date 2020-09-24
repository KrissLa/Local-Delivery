from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.menu import menu_keyboard
from loader import dp
from states.admin_state import AddAdmin
from states.menu_states import Menu
from states.seller_admin_states import SellerAdmin


@dp.message_handler(state=[SellerAdmin.RemoveItemFromStockCategory,
                           SellerAdmin.ReturnItemToStockCategory,
                           AddAdmin.WaitDeleteAdmins,
                           AddAdmin.WaitDeleteMetro,
                           AddAdmin.NewLocationMetro,
                           AddAdmin.SaveNewLocation,
                           AddAdmin.LocalObjectMetro,
                           AddAdmin.LocalObjectLocation,
                           AddAdmin.LocalObjectNameMore,
                           AddAdmin.OneMoreNewCategory,
                           AddAdmin.ItemCategory,
                           AddAdmin.ItemSize,
                           AddAdmin.ItemSizeConfirmFirst,
                           AddAdmin.ItemSizeConfirm,
                           AddAdmin.OneMoreProductSize,
                           AddAdmin.ItemConfirm,
                           AddAdmin.RemoveItemCategory,
                           AddAdmin.AdminSellerMetro,
                           AddAdmin.AdminSellerLocation,
                           AddAdmin.SellerMetro,
                           AddAdmin.SellerLocation,
                           AddAdmin.CourierMetro,
                           AddAdmin.CourierLocation,
                           AddAdmin.RemoveItemFromStockCategory,
                           AddAdmin.ReturnItemToStockCategory,
                           AddAdmin.ChangeSellerAdminMetro,
                           AddAdmin.ChangeSellerAdminLocation,
                           AddAdmin.ChangeSellerMetro,
                           AddAdmin.ChangeSellerLocation,
                           AddAdmin.ChangeCourierMetro,
                           AddAdmin.ChangeCourierLocation,
                           AddAdmin.EditMetro,
                           AddAdmin.EditItem,
                           AddAdmin.EditItemByWaitSubject,
                           AddAdmin.EditItemByAvailability,
                           AddAdmin.EditItemBySizes,
                           AddAdmin.EditItemEditSizeById,
                           ])
async def restart(message: types.Message):
    """restart"""
    await message.answer('Если Вы не хотите прерывать операцию, просто продолжите ее выше.'
                         ' Если хотите прервать, нажмите на кнопку.',
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Да, прервать.',
                                         callback_data='cancel_admin'
                                     )
                                 ]
                             ]
                         ))



@dp.message_handler(state=[Menu.WaitTime, Menu.WaitAddress, Menu.WaitCategory, Menu.WaitProduct,
                           Menu.WaitProductSize,
                           Menu.WaitProductSizeBack,
                           Menu.OneMoreOrNext, Menu.WaitUserConfirmationDelivery,
                           Menu.WaitUserConfirmationPickup, Menu.WaitPass,
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
