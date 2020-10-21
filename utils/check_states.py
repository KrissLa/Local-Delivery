import logging

from keyboards.default.menu import menu_keyboard
from loader import db

states_for_menu = '*'


async def reset_state(state, message):
    """обрабатываем выход из меню"""
    logging.info('reset')
    if await state.get_state() in ['Menu:OrderStatus', 'Menu:WaitReasonUser', 'SelectCourier:WaitReasonCourier',
                                     'SelectCourier:WaitReason', 'SelectCourier:WaitReasonActive']:
        await state.finish()
        await message.answer('Заказ не отменен',
                             reply_markup=menu_keyboard)
    elif await state.get_state() in ['Menu:WaitReview', 'Menu:WaitBonusReview']:
        await state.finish()
        await message.answer('Отзыв не сохранен',
                             reply_markup=menu_keyboard)
    elif await state.get_state() in ['SellerAdmin:DeliveryCategory', 'SellerAdmin:DeliveryProduct',
                                     'SellerAdmin:DeliveryQuantity', 'SellerAdmin:DeliveryQuantity6',
                                     'SellerAdmin:ConfirmTempOrder', 'SellerAdmin:ConfirmTempOrderRemoved',
                                     'SellerAdmin:DeliveryDate', 'SellerAdmin:DeliveryTime',
                                     'SellerAdmin:ConfirmOrder']:
        await state.finish()
        await db.delete_temp_delivery_order_by_user_id(message.from_user.id)
    elif await state.get_state() in ['Menu:WaitTime', 'Menu:WaitUserConfirmationDelivery',
                                     'Menu:WaitUserConfirmationPickup', 'Menu:WaitPass',
                                     'Menu:WaitAddress']:
        await state.finish()
        order_id = await db.get_last_order_id(message.from_user.id)
        if order_id:
            await db.delete_order_by_id(order_id)
    else:
        await state.finish()
