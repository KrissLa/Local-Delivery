from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from utils.misc import rate_limit


@dp.message_handler(text='res', state='*')
async def restart(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('стейт сброшен')


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина', #НЕ ГОТОВО
        '/menu - Показать меню', #НЕ ГОТОВО
        '/order_status - Показать статус заказа', #НЕ ГОТОВО
        '/order_status - Показать статус заказа', #НЕ ГОТОВО
        #янаработе
    ]
    await message.answer('\n'.join(text))



























#### /change_local_object admin, seller_admin


#### /change_category admin


#### /change_location admin










########### /add_admin admin
########### /delete_admin admin


########### /add_metro admin
########### /delete_metro admin


########### /add_newlocation admin
########### /delete_location admin


########### /add_local_object admin, seller_admin
########### /delete_local_object admin, seller_admin

########### /add_category admin
########### /remove_category admin


########## /add_item admin
########## /remove_item admin


########## /add_seller_admin admin
########## /remove_seller_admin admin

########## /reset_seller_admin_location admin


########## /add_seller admin, seller_admin
########## /remove_sellers admin, seller_admin

########## /reset_seller_location admin, seller_admin


######### /add_courier admin, seller_admin
######### /remove_courier admin, seller_admin

######### /reset_courier_location admin, seller_admin


######### /remove_category_from_stock admin, seller_admin
######### /return_category_to_stock admin, seller_admin



#########/remove_item_from_stock admin, seller_admin
######### /return_item_to_stock admin, seller_admin



######### /change_seller_admin_location admin


######### /change_seller_location admin


######### /change_courier_location admin


######### /edit_metro admin


####### /edit_item admin