from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from states.admin_state import AddAdmin
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


@dp.message_handler(state='*')
async def bot_echo(message: types.Message):
    await message.answer('Неизвестная команда. Воспользуйтесь командами из меню или нажмите /help')
