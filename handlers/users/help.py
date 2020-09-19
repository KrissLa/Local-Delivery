from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandHelp

from filters.users_filters import IsAdminMessage, IsSellerAdminMessage, IsSellerMessage, IsCourierMessage
from loader import dp
from utils.misc import rate_limit



@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsAdminMessage())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/first_start - Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',
        '/clear_cart - Очистить корзину / Прервать процесс оформления заказа',
        '/menu - Показать меню',
        '/order_status - Показать статус заказа',
        '/publish_post - Создать промо пост',
        '/set_about - Добавить/изменить описание компании',
        '/add_admin - Добавть админа',
        '/delete_admin - Удалить админа',
        '/add_metro - Добавить станцию метро',
        '/delete_metro - Удалить станцию метро',
        '/add_newlocation - Добавить точку продаж',
        '/delete_location - Удалить точку продаж',
        '/add_local_object - Добавить объект локальной доставки',
        '/remove_local_object - Удалить объект локальной доставки',
        '/add_category - Добавить категорию товара',
        '/remove_category - Удалить категорию товара',
        '/add_item - Добавить товар',
        '/remove_item - Удалить товар',
        '/add_seller_admin - Добавить админа локации',
        '/remove_seller_admin - Удалить админа локации',
        '/add_seller - Добавить продавца',
        '/remove_seller - Удалить продавца',
        '/add_courier - Добавить курьера',
        '/remove_courier - Удалить курьера',
        '/reset_seller_admin_location - Открепить админа локации от локации',
        '/reset_seller_location - Открепить продавца от локации',
        '/reset_courier_location - Открепить курьера от локации',
        '/remove_category_from_stock - Убрать категорию из меню',
        '/return_category_to_stock - Вернуть категорию в меню',
        '/remove_item_from_stock - Убрать товар из меню',
        '/return_item_to_stock - Вернуть товар в меню',
        '/change_seller_admin_location - Привязать админа локации к другой локации',
        '/change_seller_location - Привязать продавца к другой локации',
        '/change_courier_location - Привязать курьера к другой локации',
        '/edit_metro - Редактировать метро',
        '/edit_item - Редактировать товар',
        '/ban_user - Заблокировать пользователя',
        '/unban_user - Разблокировать пользователя',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerAdminMessage())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',
        '/clear_cart - Очистить корзину / Прервать процесс оформления заказа',
        '/menu - Показать меню',
        '/order_status - Показать статус заказа',
        '/add_new_seller - Добавить продавца',
        '/remove_sellers_ - Удалить продавца',
        '/add_new_courier - Добавить курьера',
        '/remove_courier_ - Удалить курьера',
        '/remove_category_from_stock - Убрать категорию из меню',
        '/return_category_to_stock - Вернуть категорию в меню',
        '/remove_item_from_stock - Убрать товар из меню',
        '/return_item_to_stock - Вернуть товар в меню',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerMessage())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/im_at_work - Начать принимать заказы',
        '/im_at_home - Прекратить принимать заказы',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',
        '/clear_cart - Очистить корзину / Прервать процесс оформления заказа',
        '/menu - Показать меню',
        '/order_status - Показать статус заказа',
        '/active_orders - Все принятые заказы. Отмечать заказы как готовые здесь',
        '/unaccepted_orders - Все непринятые заказы',
        '/confirm_delivery - Подтверждение выдачи заказа',
        '/confirm_readiness_bonus_orders - Отметить готовность бонусных заказов',
        '/confirm_bonus_orders - Подтверждение выдачи бонусного заказа',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsCourierMessage())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/im_at_work - Начать принимать заказы',
        '/im_at_home - Прекратить принимать заказы',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',
        '/clear_cart - Очистить корзину / Прервать процесс оформления заказа',
        '/menu - Показать меню',
        '/order_status - Показать статус заказа',
        '/all_ready_orders - Список заказов, готовых для доставке',
        '/my_orders - Список заказов, закрепленных за Вами',

    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',
        '/clear_cart - Очистить корзину / Прервать процесс оформления заказа',
        '/menu - Показать меню',
        '/order_status - Показать статус заказа',

    ]
    await message.answer('\n'.join(text))





########### /add_local_object admin, seller_admin
########### /delete_local_object admin, seller_admin


# /add_new_courier admin, seller_admin
# /remove_courier admin, seller_admin



#/remove_category_from_stock admin, seller_admin
#/return_category_to_stock admin, seller_admin



#/remove_item_from_stock admin, seller_admin
#/return_item_to_stock admin, seller_admin


# /add_new_seller admin, seller_admin
# /remove_sellers admin, seller_admin













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