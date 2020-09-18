from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начать диалог"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("menu", "Показать меню"),
        types.BotCommand("cart", "Корзина"),
        types.BotCommand("clear_cart", "Очистить корзину / Прервать процесс оформления заказа"),
        types.BotCommand("order_status", "Показать статус заказ"),
    ])