from aiogram import executor

import filters
import middlewares
from data.config import admins
from handlers import dp
from loader import db
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    filters.setup(dp)
    middlewares.setup(dp)

    await db.set_timezone()
    await db.create_table_metro()
    await db.create_table_locations()
    await db.create_table_local_objects()
    await db.create_table_categories()
    await db.create_table_products()
    await db.create_table_product_sizes()
    await db.create_table_locations_categories()
    await db.create_table_locations_products()
    await db.create_table_locations_product_sizes()
    await db.create_table_admins()
    await db.create_table_admin_sellers()
    await db.create_table_sellers()
    await db.create_table_couriers()
    await db.create_table_users()
    await db.create_table_orders()
    await db.create_table_temp_orders()
    await db.create_table_bonus_orders()
    await db.create_table_about()
    await db.create_table_delivery_categories()
    await db.create_table_delivery_products()
    await db.create_table_delivery_couriers()
    await db.create_table_delivery_orders()
    await db.create_table_temp_delivery_orders()
    await db.create_table_order_products()
    await db.create_table_delivery_order_products()
    await db.add_admin(admins, 'Главный админ')
    await set_default_commands(dp)

    await on_startup_notify(dp)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
