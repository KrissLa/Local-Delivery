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
        '1. /first_start - Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией\n',
        'Общие команды:',
        '2. /help - Получить справку',
        '3. /cart - Корзина',
        '4. /menu - Показать меню\n',
        'Команды админа:',
        '5. /publish_post - Создать промо пост',
        '6. /set_about - Добавить/изменить описание компании\n',
        'Работа с персоналом:',
        'Добавление:',
        '7. /add_admin - Добавть админа',
        '8. /add_seller_admin - Добавить админа локации',
        '9. /add_seller - Добавить продавца',
        '10. /add_courier - Добавить курьера',
        'Удаление:',
        '11. /delete_admin - Удалить админа',
        '12. /remove_seller_admin - Удалить админа локации',
        '13. /remove_seller - Удалить продавца',
        '14. /remove_courier - Удалить курьера',
        'Локации персонала:',
        '15. /reset_seller_admin_location - Открепить админа локации от локации',
        '16. /reset_seller_location - Открепить продавца от локации',
        '17. /reset_courier_location - Открепить курьера от локации',
        '18. /change_seller_admin_location - Привязать админа локации к другой локации',
        '19. /change_seller_location - Привязать продавца к другой локации',
        '20. /change_courier_location - Привязать курьера к другой локации\n',
        'Работа с локациями:',
        '21. /add_metro - Добавить станцию метро',
        '22. /add_newlocation - Добавить точку продаж',
        '23. /add_local_object - Добавить объект локальной доставки',
        '24. /delete_metro - Удалить станцию метро',
        '25. /delete_location - Удалить точку продаж',
        '26. /remove_local_object - Удалить объект локальной доставки',
        '27. /edit_metro - Редактировать метро\n',
        'Работа с категориями:',
        '28. /add_category - Добавить категорию товара',
        '29. /remove_category - Удалить категорию товара',
        '30. /remove_category_from_stock - Убрать категорию из меню',
        '31. /return_category_to_stock - Вернуть категорию в меню\n',
        'Работа с товарами:',
        '32. /add_item - Добавить товар',
        '33. /remove_item - Удалить товар',
        '34. /remove_item_from_stock - Убрать товар из меню',
        '35. /return_item_to_stock - Вернуть товар в меню',
        '36. /edit_item - Редактировать товар\n',
        'Работа с пользователями:',
        '37. /ban_user - Заблокировать пользователя',
        '38. /unban_user - Разблокировать пользователя',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerAdminMessage())
async def bot_help(message: types.Message):
    text = [
        'Общие команды: ',
        '1. /help - Получить справку',
        '2. /cart - Корзина',
        '3. /menu - Показать меню\n',
        'Работа с персоналом:',
        '4. /add_new_seller - Добавить продавца',
        '5. /remove_sellers_ - Удалить продавца',
        '6. /add_new_courier - Добавить курьера',
        '7. /remove_courier_ - Удалить курьера\n',
        'Работа с меню:',
        '8. /remove_category_from_stock - Убрать категорию из меню',
        '9. /return_category_to_stock - Вернуть категорию в меню',
        '10. /remove_item_from_stock - Убрать товар из меню',
        '11. /return_item_to_stock - Вернуть товар в меню',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerMessage())
async def bot_help(message: types.Message):
    text = [
        'Общие команды: ',
        '1. /help - Получить справку',
        '2. /cart - Корзина',
        '3. /menu - Показать меню\n',
        'Команды продавца:',
        '4. /im_at_work - Начать принимать заказы',
        '5. /im_at_home - Прекратить принимать заказы',
        '6. /unaccepted_orders - Все непринятые заказы',
        '7. /active_orders - Все принятые заказы. Отмечать заказы как готовые здесь',
        '8. /confirm_delivery - Подтверждение выдачи заказа',
        '9. /confirm_readiness_bonus_orders - Отметить готовность бонусных заказов',
        '10. /confirm_bonus_orders - Подтверждение выдачи бонусного заказа',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsCourierMessage())
async def bot_help(message: types.Message):
    text = [
        'Общие команды: ',
        '1. /help - Получить справку',
        '2. /cart - Корзина',
        '3. /menu - Показать меню\n',
        'Команды курьера:',
        '4. /im_at_work - Начать принимать заказы',
        '5. /im_at_home - Прекратить принимать заказы',
        '6. /all_ready_orders - Список заказов, готовых для доставке',
        '7. /my_orders - Список заказов, закрепленных за Вами',

    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '1. /cart - Корзина',
        '2. /menu - Показать меню',

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