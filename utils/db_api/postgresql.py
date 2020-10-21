import logging
from datetime import datetime

import asyncpg
from asyncpg.pool import Pool
from pytz import timezone

from data import config

now = datetime.now(timezone("Europe/Moscow"))


class Database:
    def __init__(self, pool):
        self.pool: Pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(
            user=config.PGUSER,
            database=config.PGDATABASE,
            password=config.PGPASSWORD,
            host=config.ip,
            port=config.PORT,
            statement_cache_size=0
        )
        return cls(pool)

    async def set_timezone(self):
        await self.pool.execute(
            "SET TIME ZONE 'Europe/Moscow';"
        )

    async def create_table_metro(self):
        """Создаем таблицу метро"""
        sql = """
        CREATE TABLE IF NOT EXISTS metro (
        metro_id SERIAL PRIMARY KEY,
        metro_name VARCHAR(255) NOT NULL,
        is_metro_available BOOLEAN NOT NULL DEFAULT true);
        """
        await self.pool.execute(sql)

    async def create_table_locations(self):
        """Создаем таблицу локаций"""
        sql = """
        CREATE TABLE IF NOT EXISTS locations (
        location_id SERIAL PRIMARY KEY,
        location_name VARCHAR(255) NOT NULL,
        location_address VARCHAR(500) NOT NULL,
        location_metro_id INT NOT NULL,
        is_location_available BOOLEAN NOT NULL DEFAULT true,
        FOREIGN KEY (location_metro_id) REFERENCES metro (metro_id) ON DELETE CASCADE ON UPDATE CASCADE);
        """
        await self.pool.execute(sql)

    async def create_table_local_objects(self):
        """Создаем таблицу локального объекта доставки"""
        sql = """
        CREATE TABLE IF NOT EXISTS local_objects (
        local_object_id SERIAL PRIMARY KEY,
        local_object_name VARCHAR(255) NOT NULL,
        local_object_location_id INT NOT NULL,
        local_object_metro_id INT NOT NULL,
        is_local_object_available BOOLEAN NOT NULL DEFAULT true,
        FOREIGN KEY (local_object_location_id) REFERENCES locations (location_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (local_object_metro_id) REFERENCES metro (metro_id) ON DELETE CASCADE ON UPDATE CASCADE);
        """
        await self.pool.execute(sql)

    async def create_table_categories(self):
        """Создаем таблицу Категорий товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(255) NOT NULL,
        is_category_available BOOLEAN NOT NULL DEFAULT true);
        """
        await self.pool.execute(sql)

    async def create_table_delivery_categories(self):
        """Создаем таблицу Категорий товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS delivery_categories (
        delivery_category_id SERIAL PRIMARY KEY,
        delivery_category_name VARCHAR(255) NOT NULL,
        is_de_category_available BOOLEAN NOT NULL DEFAULT true);
        """
        await self.pool.execute(sql)

    async def create_table_products(self):
        """Создаем таблицу Товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        product_category_id INT,
        product_name VARCHAR(500) NOT NULL,
        product_description TEXT,
        product_photo_id TEXT,
        price_1 INT,
        price_2 INT,
        price_3 INT,
        price_4 INT,
        price_5 INT,
        price_6 INT,
        is_product_available BOOLEAN NOT NULL DEFAULT true,
        FOREIGN KEY (product_category_id) REFERENCES categories (category_id) ON UPDATE CASCADE ON DELETE CASCADE);
        """
        await self.pool.execute(sql)

    async def create_table_delivery_products(self):
        """Создаем таблицу Товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS delivery_products (
        delivery_product_id SERIAL PRIMARY KEY,
        delivery_product_category_id INT,
        delivery_product_name VARCHAR(500) NOT NULL,
        delivery_price INT,
        is_de_product_available BOOLEAN NOT NULL DEFAULT true,
        FOREIGN KEY (delivery_product_category_id) REFERENCES delivery_categories (delivery_category_id) ON UPDATE CASCADE ON DELETE CASCADE);
        """
        await self.pool.execute(sql)

    async def create_table_product_sizes(self):
        """Создаем таблицу Размеров товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS product_sizes (
        size_id SERIAL PRIMARY KEY,
        size_product_id INT NOT NULL,
        size_name VARCHAR(500) NOT NULL,
        price_1 INT NOT NULL,
        price_2 INT NOT NULL,
        price_3 INT NOT NULL,
        price_4 INT NOT NULL,
        price_5 INT NOT NULL,
        price_6 INT NOT NULL,
        is_size_available BOOLEAN NOT NULL DEFAULT true,
        FOREIGN KEY (size_product_id) REFERENCES products (product_id) ON UPDATE CASCADE ON DELETE CASCADE);
        """
        await self.pool.execute(sql)

    async def create_table_locations_categories(self):
        """Создаем таблицу Локаций-Категорий товара"""
        sql = """
                CREATE TABLE IF NOT EXISTS locations_categories (
                lc_location_id INT REFERENCES locations (location_id) ON UPDATE CASCADE ON DELETE CASCADE,
                lc_category_id INT REFERENCES categories (category_id) ON UPDATE CASCADE ON DELETE CASCADE,
                is_category_in_location_available BOOLEAN NOT NULL DEFAULT true,
                CONSTRAINT locations_categories_pkey PRIMARY KEY (lc_location_id, lc_category_id));
                """
        await self.pool.execute(sql)

    async def create_table_locations_products(self):
        """Создаем таблицу Локаций-Товаров"""
        sql = """
                CREATE TABLE IF NOT EXISTS locations_products (
                lp_location_id INT REFERENCES locations (location_id) ON UPDATE CASCADE ON DELETE CASCADE,
                lp_product_id INT REFERENCES products (product_id) ON UPDATE CASCADE ON DELETE CASCADE,
                is_product_in_location_available BOOLEAN NOT NULL DEFAULT true,
                CONSTRAINT locations_products_pkey PRIMARY KEY (lp_location_id, lp_product_id));
                """
        await self.pool.execute(sql)

    async def create_table_locations_product_sizes(self):
        """Создаем таблицу Локаций-Товаров"""
        sql = """
                CREATE TABLE IF NOT EXISTS locations_product_sizes (
                lps_location_id INT REFERENCES locations (location_id) ON UPDATE CASCADE ON DELETE CASCADE,
                lps_size_product_id INT REFERENCES product_sizes (size_id) ON UPDATE CASCADE ON DELETE CASCADE,
                is_size_product_in_location_available BOOLEAN NOT NULL DEFAULT true,
                CONSTRAINT locations_size_pkey PRIMARY KEY (lps_location_id, lps_size_product_id));
                """
        await self.pool.execute(sql)

    async def create_table_admins(self):
        """Создаем таблицу Админов"""
        sql = """
                CREATE TABLE IF NOT EXISTS admins (
                admin_id SERIAL PRIMARY KEY,
                admin_telegram_id INT NOT NULL UNIQUE,
                admin_email TEXT,
                admin_name VARCHAR(255)
                );
                """
        await self.pool.execute(sql)

    async def create_table_admin_sellers(self):
        """Создаем таблицу Админов-продавцов"""
        sql = """
                CREATE TABLE IF NOT EXISTS admin_sellers (
                admin_seller_id SERIAL PRIMARY KEY,
                admin_seller_telegram_id INT NOT NULL UNIQUE,
                admin_seller_name VARCHAR(255) NOT NULL,
                admin_seller_email TEXT,
                admin_seller_metro_id INT,
                admin_seller_location_id INT,
                FOREIGN KEY (admin_seller_metro_id) REFERENCES metro (metro_id) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (admin_seller_location_id) REFERENCES locations (location_id) ON DELETE SET NULL ON UPDATE CASCADE
                );
        """
        await self.pool.execute(sql)

    async def create_table_sellers(self):
        """Создаем таблицу Продавцов"""
        sql = """
                CREATE TABLE IF NOT EXISTS sellers (
                seller_id SERIAL PRIMARY KEY,
                seller_telegram_id INT NOT NULL UNIQUE,
                seller_name VARCHAR (255) NOT NULL,
                seller_metro_id INT,
                seller_location_id INT,
                seller_status BOOLEAN NOT NULL DEFAULT false,
                FOREIGN KEY (seller_metro_id) REFERENCES metro (metro_id) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (seller_location_id) REFERENCES locations (location_id) ON DELETE SET NULL ON UPDATE CASCADE
                );
                """
        await self.pool.execute(sql)

    async def create_table_couriers(self):
        """Создаем таблицу Курьеров"""
        sql = """
                CREATE TABLE IF NOT EXISTS couriers (
                courier_id SERIAL PRIMARY KEY,
                courier_telegram_id INT NOT NULL UNIQUE,
                courier_name VARCHAR(255) NOT NULL,
                courier_metro_id INT,
                courier_location_id INT,
                courier_status BOOLEAN NOT NULL DEFAULT false,
                FOREIGN KEY (courier_metro_id) REFERENCES metro (metro_id) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (courier_location_id) REFERENCES locations (location_id) ON DELETE SET NULL ON UPDATE CASCADE
                );
                """
        await self.pool.execute(sql)

    async def create_table_delivery_couriers(self):
        """Создаем таблицу Курьеров"""
        sql = """
                CREATE TABLE IF NOT EXISTS delivery_couriers (
                delivery_courier_id SERIAL PRIMARY KEY,
                delivery_courier_telegram_id INT NOT NULL UNIQUE,
                delivery_courier_name VARCHAR(255) NOT NULL,
                delivery_courier_status BOOLEAN NOT NULL DEFAULT true
                );
                """
        await self.pool.execute(sql)

    async def create_table_users(self):  # Добавить фото
        """Создаем таблицу пользователей"""
        sql = """
           CREATE TABLE IF NOT EXISTS users (
           user_id SERIAL PRIMARY KEY,
           user_telegram_id INT NOT NULL UNIQUE,
           user_metro_id INT,
           user_location_id INT,
           user_local_object_id INT,
           user_address TEXT,
           user_phone_number VARCHAR (30),
           number_of_orders INT NOT NULL DEFAULT 0,
           inviter_id INT,
           number_of_referrals INT NOT NULL DEFAULT 0,
           number_of_referral_orders INT NOT NULL DEFAULT 0,
           bonus INT NOT NULL DEFAULT 0,
           is_banned BOOLEAN NOT NULL DEFAULT false,
           reason_for_ban TEXT,
           FOREIGN KEY (user_metro_id) REFERENCES metro (metro_id) ON DELETE SET NULL,
           FOREIGN KEY (user_location_id) REFERENCES locations (location_id) ON DELETE SET NULL,
           FOREIGN KEY (user_local_object_id) REFERENCES local_objects (local_object_id) ON DELETE SET NULL
           );
           """
        await self.pool.execute(sql)

    async def create_table_orders(self):
        """Создаем таблицу заказов"""
        sql = """
            CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            order_user_id INT NOT NULL,
            order_seller_id INT,
            order_courier_id INT,
            order_date DATE,
            order_year INT,
            order_month INT,
            order_created_at TIME,
            order_accepted_at TIME,
            order_canceled_at TIME,
            order_time_for_delivery TIME,
            order_delivered_at TIME,
            order_deliver_through INT,
            order_local_object_id INT,
            order_address TEXT,
            order_pass_to_courier TEXT,
            order_final_price INT,
            order_delivery_method order_method,
            order_status order_status,
            order_review TEXT,
            order_reason_for_rejection TEXT
            );
            """
        try:
            await self.pool.execute("CREATE TYPE order_method AS ENUM ('Доставка', 'Самовывоз');")
        except asyncpg.exceptions.DuplicateObjectError as err:
            logging.error(err)
        try:
            await self.pool.execute(
                "CREATE TYPE order_status AS ENUM ('Ожидание пользователя', 'Ожидание продавца',"
                "'Принят', 'Приготовлен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером', "
                "'Выполнен');")
        except asyncpg.exceptions.DuplicateObjectError as err:
            logging.error(err)
        await self.pool.execute(sql)

    async def create_table_order_products(self):
        """Создаем таблицу заказов"""
        sql = """
           CREATE TABLE IF NOT EXISTS order_products (
           op_order_id INT,
           op_product_id INT,
           op_size_id INT,
           op_product_name VARCHAR(255),
           op_quantity INT,
           op_price_per_unit INT,
           op_price INT,
           FOREIGN KEY (op_order_id) REFERENCES orders (order_id) ON DELETE CASCADE ON UPDATE CASCADE
           );
           """
        await self.pool.execute(sql)

    async def create_table_delivery_orders(self):
        """Создаем таблицу заказов"""
        sql = f"""
           CREATE TABLE IF NOT EXISTS delivery_orders (
           delivery_order_id SERIAL PRIMARY KEY,
           delivery_order_seller_admin_id INT NOT NULL,
           delivery_order_admin_id INT,
           delivery_order_courier_id INT,
           delivery_order_location_id INT NOT NULL,
           delivery_order_created_at timestamp DEFAULT now() NOT NULL,
           delivery_order_canceled_at timestamp,
           delivery_order_changed_at timestamp,
           delivery_order_delivered_at timestamp,
           delivery_order_day_for_delivery date,
           dlivery_order_time_for_delivery time,
           delivery_order_datetime TIMESTAMP,
           delivery_order_time_info delivery_time,
           delivery_order_final_price INT,
           delivery_order_status delivery_or_status
           );
           """
        try:
            await self.pool.execute(
                "CREATE TYPE delivery_or_status AS ENUM ('Ожидание подтверждения', 'Ожидание подтверждения курьером', "
                "'Заказ подтвержден', 'Отменен клиентом', 'Отменен поставщиком', 'Курьер не назначен', "
                "'Заказ выполнен');")
        except asyncpg.exceptions.DuplicateObjectError as err:
            logging.error(err)
        try:
            await self.pool.execute(
                "CREATE TYPE delivery_time AS ENUM ('c 08-00 до 10-00', 'с 10-00 до 12-00', 'с 12-00 до 14-00', "
                "'с 14-00 до 16-00', 'с 16-00 до 18-00', 'с 18-00 до 20-00');")
        except asyncpg.exceptions.DuplicateObjectError as err:
            logging.error(err)
        await self.pool.execute(sql)

    async def create_table_delivery_order_products(self):
        """Создаем таблицу заказов"""
        sql = """
           CREATE TABLE IF NOT EXISTS delivery_order_products (
           dop_order_id INT not null,
           dop_product_id INT,
           dop_product_name VARCHAR(255),
           dop_quantity INT,
           dop_price_per_unit INT,
           dop_price INT,
           FOREIGN KEY (dop_order_id) REFERENCES delivery_orders (delivery_order_id) ON DELETE CASCADE ON UPDATE CASCADE
           );
           """
        await self.pool.execute(sql)

    async def create_table_temp_orders(self):
        """Создаем таблицу заказов"""
        sql = """
           CREATE TABLE IF NOT EXISTS temp_orders (
           temp_order_id SERIAL PRIMARY KEY,
           temp_order_user_telegram_id INT NOT NULL,
           product_id INT NOT NULL,
           size_id INT,
           product_name VARCHAR(255) NOT NULL,
           product_price INT NOT NULL,
           quantity INT NOT NULL,
           order_price INT NOT NULL
           );
           """
        await self.pool.execute(sql)

    async def create_table_temp_delivery_orders(self):
        """Создаем таблицу заказов"""
        sql = """
           CREATE TABLE IF NOT EXISTS temp_delivery_orders (
           temp_delivery_order_id SERIAL PRIMARY KEY,
           temp_delivery_order_user_telegram_id INT NOT NULL,
           delivery_product_id INT NOT NULL,
           delivery_product_name VARCHAR(255) NOT NULL,
           delivery_product_price INT NOT NULL,
           delivery_quantity INT NOT NULL,
           delivery_order_price INT NOT NULL
           );
           """
        await self.pool.execute(sql)

    async def create_table_bonus_orders(self):
        """Создаем таблицу бонусных заказов"""
        sql = """
                   CREATE TABLE IF NOT EXISTS bonus_orders (
                   bonus_order_id SERIAL PRIMARY KEY,
                   bonus_order_location_id INT NOT NULL,
                   bonus_order_date DATE,
                   bonus_order_user_id INT NOT NULL,
                   bonus_order_seller_id INT,
                   bonus_order_created_at TIME,
                   bonus_order_accepted_at TIME,
                   bonus_order_canceled_at TIME,
                   bonus_order_delivered_at TIME,
                   bonus_order_quantity INT NOT NULL,
                   bonus_order_status VARCHAR(255),
                   bonus_order_review TEXT,
                   bonus_order_reason_for_rejection TEXT
                   );
                   """
        await self.pool.execute(sql)

    async def create_table_about(self):
        """Создаем таблицу о компании"""
        sql = """
                   CREATE TABLE IF NOT EXISTS about (
                   info TEXT
                   );
                   """
        await self.pool.execute(sql)

    ##### FILTERS ####

    async def is_admin(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT admin_telegram_id FROM admins WHERE admin_telegram_id = {user_id})'
        )

    async def is_seller_admin(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT admin_seller_telegram_id FROM admin_sellers WHERE admin_seller_telegram_id = {user_id}) '
        )

    async def is_seller(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT seller_telegram_id FROM sellers WHERE seller_telegram_id = {user_id})'
        )

    async def is_courier(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT courier_telegram_id FROM couriers WHERE courier_telegram_id = {user_id})'
        )

    async def is_delivery_courier(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT delivery_courier_telegram_id FROM delivery_couriers WHERE delivery_courier_telegram_id = {user_id})'
        )

    async def is_client(self, user_id):
        """Проверяем админ или нет"""
        return await self.pool.fetchval(
            f'SELECT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_id})'
        )

    async def has_location(self, user_id):
        """Проверяем админ или нет"""
        location_id = await self.pool.fetchval(
            f'SELECT user_location_id FROM users WHERE user_telegram_id = {user_id}'
        )
        if location_id:
            return True
        else:
            return False

    async def has_local_object(self, user_id):
        """Проверяем админ или нет"""
        local_object = await self.pool.fetchval(
            f'SELECT user_local_object_id FROM users WHERE user_telegram_id = {user_id}'
        )
        if local_object:
            return True
        else:
            return False

    async def has_metro(self, user_id):
        """Проверяем админ или нет"""
        metro = await self.pool.fetchval(
            f'SELECT user_metro_id FROM users WHERE user_telegram_id = {user_id}'
        )
        if metro:
            return True
        else:
            return False

    async def is_banned(self, user_id):
        """Проверяем забанен ли"""
        return await self.pool.fetchval(
            f"""SELECT is_banned FROM users WHERE user_telegram_id={user_id}"""
        )

    async def has_location_seller_admin(self, user_id):
        """Проверяем админ или нет"""
        status = await self.pool.fetchval(
            f'SELECT admin_seller_location_id FROM admin_sellers WHERE admin_seller_telegram_id = {user_id}'
        )
        if status:
            return True
        return False

    async def item_is_available(self, product_id):
        """Проверяем в продаже товар или нет"""
        return await self.pool.fetchval(
            f"""
    SELECT is_product_available 
    FROM products 
    WHERE product_id={product_id}"""
        )

    async def product_has_size(self, product_id):
        """Проверяем есть ли у товара размеры"""
        return await self.pool.fetchval(
            f"""
    SELECT EXISTS(SELECT size_product_id FROM product_sizes WHERE size_product_id={product_id})"""
        )

    async def order_has_review(self, order_id):
        """Проверяем есть ли уже отзыв к заказу"""
        rev = await self.pool.fetchval(f"select order_review from orders where order_id ={order_id}")
        if rev:
            return True
        return False

    async def bonus_order_has_review(self, order_id):
        """Проверяем есть ли уже отзыв к заказу"""
        rev = await self.pool.fetchval(f"select bonus_order_review from bonus_orders where bonus_order_id ={order_id}")
        if rev:
            return True
        return False

    async def is_last_delivery_order(self, user_id, order_id):
        """Проверяем последний ли товар"""
        return order_id == await self.pool.fetchval(f"""
    SELECT temp_delivery_order_id 
    FROM temp_delivery_orders
    WHERE temp_delivery_order_user_telegram_id = {user_id} 
    ORDER BY - temp_delivery_order_id""")

    async def is_user_owner(self, user_id, order_id):
        """Проверяем пользователь владелец заказа или нет"""
        return user_id == await self.pool.fetchval(f"""
    select admin_seller_telegram_id 
    from admin_sellers 
    where admin_seller_id = (SELECT delivery_order_seller_admin_id 
                                        FROM delivery_orders 
                                        WHERE delivery_order_id = {order_id})""")

    ##### FILTERS ####

    ##### GET ########

    ## products ###

    async def get_delivery_products_list(self, category_id):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""SELECT delivery_product_id, delivery_product_name 
    FROM delivery_products 
    WHERE delivery_product_category_id={category_id}
    ORDER BY delivery_product_id"""
        )

    async def get_delivery_product_by_id(self, product_id):
        """Получаем название товара по id"""
        return await self.pool.fetchrow(
            f"""SELECT * 
    FROM delivery_products 
    WHERE delivery_product_id = {product_id}"""
        )

    async def get_delivery_products_for_return_to_stock(self, category_id):
        """Выбираем товары из категории"""
        return await self.pool.fetch(
            f"""
    SELECT delivery_product_id, delivery_product_name 
    FROM delivery_products
    WHERE delivery_product_category_id = {category_id} 
    AND is_de_product_available = false 
    ORDER BY delivery_product_id"""
        )

    async def get_delivery_products_for_remove_from_stock(self, category_id):
        """Выбираем товары из категории чтобы свять с продажи"""
        return await self.pool.fetch(
            f"""
    SELECT delivery_product_id, delivery_product_name 
    FROM delivery_products
    WHERE delivery_product_category_id = {category_id} 
    AND is_de_product_available = true 
    ORDER BY delivery_product_id"""
        )

    async def get_product_info(self, product_id):
        """Получаем информацию о товаре"""
        return await self.pool.fetchrow(
            f"""
    SELECT * 
    FROM products 
    WHERE product_id = {product_id}"""
        )

    async def get_product_sizes(self, product_id):
        """Получаем размеры товара"""
        return await self.pool.fetch(
            f"""
    SELECT * 
    FROM product_sizes 
    WHERE size_product_id = {product_id}"""
        )

    async def get_products_list(self, category_id):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""
    SELECT product_id, product_name 
    FROM products  
    WHERE product_category_id={category_id}
    ORDER BY product_id"""
        )

    async def get_products_for_remove_from_stock(self, category_id):
        """Выбираем товары из категории чтобы свять с продажи"""
        return await self.pool.fetch(
            f"""
    SELECT product_id, product_name 
    FROM products
    WHERE product_category_id = {category_id} 
    AND is_product_available = true 
    ORDER BY product_id"""
        )

    async def get_products_for_return_to_stock(self, category_id):
        """Выбираем товары из категории"""
        return await self.pool.fetch(
            f"""
    SELECT product_id, product_name 
    FROM products
    WHERE product_category_id = {category_id} 
    AND is_product_available = false 
    ORDER BY product_id"""
        )

    async def get_size_info_by_id(self, size_id):
        """Получаем инфу о размере"""
        return await self.pool.fetchrow(
            f"""
    SELECT * 
    FROM product_sizes 
    WHERE size_id = {size_id}"""
        )

    async def get_product_for_user_location_id(self, user_id, category_id):
        """Получаем список доступных товаров в локации пользователя"""
        prod_result = []
        sql = f"""
    SELECT products.product_name, products.product_id, price_1
    FROM locations_products 
    JOIN products ON locations_products.lp_product_id=products.product_id
    WHERE products.product_category_id = {category_id}
    AND locations_products.lp_location_id=
    (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
    AND locations_products.is_product_in_location_available = true 
    AND products.is_product_available = true
    ORDER BY product_id;
    """
        products_list = await self.pool.fetch(sql)
        for prod in products_list:
            if prod['price_1']:
                prod_result.append(prod)
            else:
                with_size = await self.pool.fetchval(
                    f"""
    SELECT EXISTS(SELECT size_id FROM product_sizes  WHERE size_product_id = {prod['product_id']})"""
                )
                if with_size:
                    prod_result.append(prod)
        return prod_result

    async def get_product_info_by_id(self, product_id, user_id):
        """Получаем подробную информацию о товаре"""
        sql = f"""
    SELECT product_category_id, product_name, product_description, product_photo_id, price_1, 
            price_2, price_3, price_4, price_5, price_6  
    from products 
    where product_id = {product_id};
    """
        sql2 = f"""
    SELECT product_sizes.size_id, product_sizes.size_name, product_sizes.price_1, product_sizes.size_product_id
    FROM locations_product_sizes 
    JOIN product_sizes ON locations_product_sizes.lps_size_product_id=product_sizes.size_id
    WHERE product_sizes.size_product_id = {product_id}
    AND locations_product_sizes.lps_location_id = (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
    AND product_sizes.is_size_available = true
    AND locations_product_sizes.is_size_product_in_location_available=true
    ORDER BY size_product_id;
    """
        sql3 = f"""
    SELECT product_category_id, product_name, product_description, product_photo_id 
    from products 
    where product_id = {product_id};
    """
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT size_product_id FROM product_sizes WHERE size_product_id = {product_id});"):

            result = await self.pool.fetchrow(sql)
        else:
            result = {
                'product_info': await self.pool.fetchrow(sql3),
                'list_of_sizes': await self.pool.fetch(sql2)
            }

        return result

    async def get_size_info(self, size_id):
        """Получаем информацию о размере"""
        return await self.pool.fetchrow(
            f"""
    SELECT size_name, size_product_id, price_1, price_2, price_3, price_4, price_5, price_6 
    from product_sizes 
    where size_id = {size_id}"""
        )

    async def get_product_name(self, product_id):
        """Получаем название товара"""
        return await self.pool.fetchval(f"""
    SELECT product_name 
    FROM products 
    WHERE product_id = {product_id}""")

    async def get_products_for_stock_in_location(self, location_id, category_id, status):
        """Получаем товары из категории"""
        return await self.pool.fetch(f"""
    SELECT product_id, product_name 
    FROM categories
    JOIN products ON product_category_id=category_id
    JOIN locations_products ON lp_product_id = product_id
    WHERE is_product_in_location_available = {status} 
    AND lp_location_id = {location_id}
    AND category_id = {category_id}
    ORDER BY product_category_id;""")

    ## products ###

    ## category ##

    async def get_delivery_category_name_by_id(self, category_id):
        """Получааем название категории"""
        return await self.pool.fetchval(
            f"""
    SELECT delivery_category_name 
    FROM delivery_categories 
    WHERE delivery_category_id = {category_id}"""
        )

    async def get_category_name_by_id(self, category_id):
        """Получааем название категории"""
        return await self.pool.fetchval(
            f"""
    SELECT category_name 
    FROM categories 
    WHERE category_id = {category_id}"""
        )

    async def get_category_list(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM categories
    ORDER BY category_id"""
        )

    async def get_list_of_categories(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            """
    SELECT *
    FROM categories
    ORDER BY category_id"""
        )  ### del

    async def get_list_of_categories_with_items(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT category_id, category_name
    FROM categories 
    JOIN products on product_category_id=category_id
    ORDER BY category_id;"""
        )

    async def get_category_for_admin_true(self):
        """Выбираем все категории, доступные для проажи"""
        return await self.pool.fetch(
            f"""
    SELECT category_id, category_name 
    FROM categories 
    WHERE is_category_available=true 
    ORDER BY category_id"""
        )

    async def get_category_for_admin_false(self):
        """Выбираем все категории, снятые с проажи"""
        return await self.pool.fetch(
            f"""
    SELECT category_id, category_name 
    FROM categories 
    WHERE is_category_available=false 
    ORDER BY category_id"""
        )

    async def get_category_for_remove_item_from_stock(self):
        """Выбираем все категории, в которых есть товары в продаже"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT  category_id, category_name 
    FROM  products
    JOIN categories ON product_category_id=category_id
    WHERE is_product_available = true 
    ORDER BY category_id"""
        )

    async def get_category_for_admin(self):
        """Выбираем все категории, в которых есть снятые с продажи товары"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT category_id, category_name 
    FROM categories
    JOIN products ON product_category_id=category_id
    WHERE is_product_available = false 
    ORDER BY category_id"""
        )

    async def get_categories_with_products(self):
        """Все категории, в которых есть товары"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT category_id, category_name 
    FROM categories
    JOIN products ON product_category_id=category_id 
    ORDER BY category_id"""
        )  ### del

    async def get_categories_for_user_location_id(self, user_id):
        """Получаем список доступных категорий в локации пользователя"""
        sql = f"""
    SELECT DISTINCT categories.category_name, categories.category_id
    FROM locations_categories 
    JOIN categories ON locations_categories.lc_category_id=categories.category_id
    JOIN products ON product_category_id=category_id
    WHERE locations_categories.lc_location_id=
    (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
    AND locations_categories.is_category_in_location_available = true 
    AND categories.is_category_available = true
    AND is_product_available = true
    ORDER BY category_id;
    """
        return await self.pool.fetch(sql)

    async def get_category_for_stock_item_in_location(self, location_id, status):
        """Достаем категории с товарами"""
        return await self.pool.fetch(f"""
    SELECT DISTINCT category_id, category_name 
    FROM categories
    JOIN products ON product_category_id=category_id
    JOIN locations_products ON lp_product_id = product_id
    WHERE is_product_in_location_available = {status} 
    AND lp_location_id = {location_id}
    ORDER BY category_id;""")

    async def get_categories_in_stock_by_location(self, location_id, status):
        """Получаем категорию, доступную для пользователя"""
        return await self.pool.fetch(f"""
    SELECT category_id, category_name 
    FROM locations_categories
    JOIN categories  ON lc_category_id=category_id
    WHERE  lc_location_id = {location_id}
    AND is_category_in_location_available = {status}
    ORDER BY category_id;""")

    ## category ##

    ## users ##

    async def get_users_id(self):
        """Получаем список пользователей"""
        return await self.pool.fetch(
            f"""
    SELECT user_telegram_id 
    FROM users"""
        )

    async def get_user_location_id(self, user_id):
        """Получаем id локации пользователя"""
        return await self.pool.fetchval(
            f"""
    SELECT user_location_id 
    FROM users 
    WHERE user_telegram_id = {user_id}"""
        )

    async def get_user_id(self, user_tg_id):
        """Пытаемся получить пользователя из таблицы"""
        return await self.pool.fetchval(
            f"""
    select user_id 
    from users 
    where user_telegram_id = {user_tg_id}"""
        )

    async def get_reason_for_ban(self, user_id):
        """Проверяем забанен ли"""
        return await self.pool.fetchval(
            f"""
    SELECT reason_for_ban 
    FROM users 
    WHERE user_telegram_id={user_id}"""
        )

    async def get_user_profile_info(self, user_id):
        """Получаем информацию о пользователе"""
        return await self.pool.fetchrow(
            f"""
    SELECT users.user_telegram_id, local_objects.local_object_name, users.user_address
    FROM users
    JOIN local_objects ON local_objects.local_object_id=users.user_local_object_id
    WHERE users.user_telegram_id = {user_id};
    """
        )

    async def get_bonus_and_location_address(self, user_id):
        """Получаем количество бонусов и адес локации"""
        return await self.pool.fetchrow(
            f"""
    SELECT bonus, location_address
    FROM users 
    JOIN locations ON user_location_id=location_id
    WHERE user_telegram_id = {user_id};"""
        )

    async def get_user_tg_id(self, order_id):
        """Получаем id клиента"""
        return await self.pool.fetchval(f"""
    SELECT user_telegram_id 
    FROM users 
    WHERE user_id = (select order_user_id from orders where order_id={order_id})""")

    async def get_user_address_data(self, user_id):
        """Получаем инфу о пользователе для создания заказа"""
        return await self.pool.fetchrow(f"""
    SELECT user_id, user_local_object_id, user_address, location_address, local_object_name
    FROM users 
    JOIN locations ON user_location_id=location_id
    JOIN local_objects ON local_object_id=user_local_object_id
    WHERE user_telegram_id = {user_id};""")

    async def get_bonus_order_user(self, bonus_order_id):
        """Получаем id пользователя"""
        return await self.pool.fetchval(f"""
    select user_telegram_id 
    from users
    where user_id = (select bonus_order_user_id 
                    from bonus_orders 
                    where bonus_order_id={bonus_order_id})""")

    async def get_user(self, user_id):
        """Пытаемся получить пользователя из таблицы"""
        return await self.pool.fetchval(
            f"""select user_telegram_id from users where user_telegram_id = {user_id}""")

    ## users ##

    ## metro ##

    async def get_metro_name_by_id(self, metro_id):
        """Получаем название ветки метро по id"""
        return await self.pool.fetchval(
            f"""
    SELECT metro_name 
    FROM metro 
    WHERE metro_id = {metro_id}"""
        )

    async def get_last_metro_id(self):
        """Получаем id последней добавленной ветки метро"""
        return await self.pool.fetchval(
            """
    SELECT metro_id 
    FROM metro 
    ORDER BY -metro_id"""
        )

    async def get_metro_name_by_location_metro_id(self, location_metro_id):  #### del
        """Получаем название ветки метро"""
        return await self.pool.fetchval(
            f"""
    SELECT metro_name 
    FROM metro 
    WHERE metro_id = {location_metro_id}"""
        )  ##### del

    async def get_metro_name_by_metro_id(self, metro_id):
        """Получаем название станции метро по его id"""
        return await self.pool.fetchval(f"SELECT metro_name FROM metro WHERE metro_id = {metro_id}")

    async def get_all_metro(self):
        """Получаем список метро"""
        return await self.pool.fetch("SELECT * FROM metro ORDER BY metro_id")

    async def get_available_metro(self):
        """Получаем список доступных станций метро"""
        return await self.pool.fetch("""
    SELECT DISTINCT metro_id, metro_name  
    FROM metro 
    JOIN locations ON location_metro_id = metro_id
    JOIN local_objects ON local_object_location_id = location_id
    where is_metro_available = TRUE 
    AND is_local_object_available = true ORDER BY metro_id""")

    ## metro ##

    ## location ##

    async def get_location_name_by_id(self, location_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchval(
            f"""
    SELECT location_name  
    FROM locations 
    WHERE location_id = {location_id}"""
        )

    async def get_list_of_locations(self):
        """Получаем список локаций"""
        return await self.pool.fetch(
            """
    SELECT *
    FROM locations 
    ORDER BY location_metro_id"""
        )

    async def get_local_objects_list(self):
        """Получаем список объектов доставки"""
        return await self.pool.fetch(
            f"""
    SELECT * 
    FROM local_objects 
    JOIN locations ON locations.location_id = local_objects.local_object_location_id
    ORDER BY local_object_location_id
    """
        )

    async def get_all_locations(self):
        """Выбираем локации в которых были заказы"""
        return await self.pool.fetch("""
    select distinct location_id, location_name
    from orders
    join local_objects on local_object_id = order_local_object_id
    join locations on location_id = local_object_location_id
    order by location_id
            """)

    async def get_all_delivery_locations(self):
        """Выбираем локации в которых были заказы"""
        return await self.pool.fetch("""
    select distinct location_id, location_name
    from delivery_orders
    join locations on location_id = delivery_order_location_id
    order by location_id
            """)

    async def get_admin_location_id(self, location_id):
        """Получаем id локации админа локации"""
        return await self.pool.fetchrow(f"""
    select location_id, location_name
    from locations
    where location_id = {location_id}""")

    async def get_objects(self):
        """Получаем список с названиями точек доставки"""
        return await self.pool.fetch(
            f"""
    SELECT local_object_name 
    from local_objects"""
        )

    async def get_local_object_data_by_id(self, local_object_id):
        """Получаем информацию об объекте доставки по id"""
        return await self.pool.fetchrow(f"""
    SELECT local_object_name, local_object_location_id, local_object_metro_id  
    FROM local_objects 
    WHERE local_object_id = {local_object_id}""")

    async def get_delivery_address_for_seller_admin(self, user_id):
        """Получаем адрес доставки оптового заказа"""
        return await self.pool.fetchrow(f"""
    SELECT metro.metro_name, locations.location_name, locations.location_address
    from locations
    JOIN metro ON location_metro_id=metro_id
    WHERE locations.location_id = (SELECT admin_seller_location_id 
    							   FROM admin_sellers
    							   WHERE admin_seller_telegram_id = {user_id});""")

    async def get_locations_by_metro_id(self, metro_id):
        """Получаем список доступных локаций около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT location_id, location_name  FROM locations where location_metro_id = {metro_id}")

    async def get_available_local_objects(self, metro_id):
        """Получаем список доступных объектов доставки около заданной станции метро"""
        return await self.pool.fetch(f"""
    SELECT local_object_id, local_object_name  
    FROM local_objects 
    where local_object_metro_id = {metro_id} 
    AND is_local_object_available = TRUE""")

    ## location ##

    ## seller_admins ##

    async def get_seller_admin_name_id(self, seller_admin_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""
    SELECT admin_seller_name, admin_seller_telegram_id 
    FROM admin_sellers
    WHERE admin_seller_id={seller_admin_id}"""
        )

    async def get_seller_admins_list(self):
        """Получаем список админов локаций"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM admin_sellers
    ORDER BY admin_seller_id"""
        )

    async def get_seller_admin_location(self, user_id):
        """Получаем локацию админа локации"""
        return await self.pool.fetchval(
            f"""
    SELECT admin_seller_location_id 
    FROM admin_sellers
    WHERE admin_seller_telegram_id = {user_id}"""
        )

    async def get_email_seller(self, user_id):
        """Получаем email админа локации"""
        return await self.pool.fetchval(f"""
    select admin_seller_email 
    from admin_sellers 
    where admin_seller_telegram_id = {user_id}""")

    async def get_seller_admin_location_id(self, user_id):
        """Получаем id локации админа локации"""
        return await self.pool.fetchrow(f"""
    select location_id, location_name
    from admin_sellers
    join  locations on admin_seller_location_id = location_id
    where admin_seller_telegram_id = {user_id}""")

    async def get_seller_admin_tg_id(self, order_id):
        """Получаем id админа локации"""
        return await self.pool.fetchval(f"""
    select admin_seller_telegram_id 
    from admin_sellers
    where admin_seller_location_id = (select local_object_location_id from local_objects
    where local_object_id = (select order_local_object_id from orders where order_id={order_id}))""")

    async def get_location_by_seller_admin_id(self, seller_admin_id):
        """Получаем id локации по id seller-admina"""
        return await self.pool.fetchrow(f"""
    SELECT admin_seller_location_id, admin_seller_metro_id 
    FROM admin_sellers 
    WHERE admin_seller_telegram_id = {seller_admin_id}""")

    async def get_location_for_seller_admin(self, seller_admin_id):
        """Получаем id локации по id seller-admina"""
        return await self.pool.fetchval(f"""
    SELECT admin_seller_location_id 
    FROM admin_sellers 
    WHERE admin_seller_telegram_id = {seller_admin_id}""")

    async def get_seller_admin_data(self, user_id):
        """Получаем инфу об админе локации"""
        return await self.pool.fetchval(f"""
    select admin_seller_name 
    from admin_sellers 
    where admin_seller_telegram_id = {user_id}""")

    ## seller_admins ##

    ## sellers ##

    async def get_seller_name_id(self, seller_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""
    SELECT seller_name, seller_telegram_id 
    FROM sellers
    WHERE seller_id={seller_id}"""
        )

    async def get_seller_list(self):
        """Получаем список Продавцов локаций"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM sellers
    ORDER BY seller_id"""
        )

    async def get_sellers_id_for_location(self, location_id):
        """Получаем доступных продавцов в локации"""
        return await self.pool.fetch(
            f"""
    SELECT seller_telegram_id 
    FROM sellers 
    WHERE seller_location_id = {location_id} 
    AND seller_status = true""")

    async def get_seller_tg_id(self, seller_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(f"""
    select seller_telegram_id 
    from sellers 
    where seller_id={seller_id}""")

    async def get_sellers_list_by_location(self, location_id):
        """Получаем список продавцов в локации"""
        return await self.pool.fetch(f"""
    SELECT seller_id, seller_name, seller_telegram_id 
    FROM sellers 
    WHERE seller_location_id={location_id}""")

    async def get_seller_location(self, seller_id):
        """Получаем id локации продацва"""
        return await self.pool.fetchval(
            f"""SELECT seller_location_id FROM sellers WHERE seller_id = {seller_id}"""
        )

    async def get_seller_location_id(self, seller_id):
        """Получаем id локации продавца"""
        return await self.pool.fetchval(
            f'SELECT seller_location_id FROM sellers WHERE seller_telegram_id = {seller_id}'
        )

    ## sellers ##

    ## couriers ##

    async def get_courier_name_id(self, courier_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""
    SELECT courier_name, courier_telegram_id 
    FROM couriers
    WHERE courier_id={courier_id}"""
        )

    async def get_delivery_couriers(self):
        """Получаем список курьеров, закрепленных за локацией"""
        return await self.pool.fetch(f"""
    SELECT delivery_courier_id, delivery_courier_telegram_id, delivery_courier_name
    FROM delivery_couriers 
    WHERE delivery_courier_status = true
"""

                                     )

    async def get_courier_list(self):
        """Получаем список Продавцов локаций"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM couriers
    ORDER BY courier_id"""
        )

    async def get_delivery_courier_list(self):
        """Получаем список Продавцов локаций"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM delivery_couriers
    ORDER BY delivery_courier_id"""
        )

    async def get_delivery_courier_name(self, courier_tg_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(f"""
    SELECT delivery_courier_name 
    FROM delivery_couriers
    WHERE delivery_courier_telegram_id = {courier_tg_id}
"""

                                        )

    async def get_couriers_list(self, location_id):
        """Получаем список курьеров, закрепленных за локацией"""
        return await self.pool.fetch(
            f"""
    SELECT courier_name 
    FROM couriers 
    WHERE courier_location_id = {location_id} 
    AND courier_status = true"""
        )

    async def get_courier_tg_id(self, courier_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(f"""
    select courier_telegram_id 
    from couriers 
    where courier_id={courier_id}""")

    async def get_courier_list_by_location(self, location_id):
        """Получаем список курьеров в локации"""
        return await self.pool.fetch(f"""
    SELECT courier_id, courier_name, courier_telegram_id 
    FROM couriers 
    WHERE courier_location_id={location_id}""")

    async def get_delivery_courier_tg_id(self, order_id):
        """Получаем тг id админа"""
        return await self.pool.fetchval(f"""
    select delivery_courier_telegram_id 
    from delivery_couriers
    where delivery_courier_id=(SELECT delivery_order_courier_id 
                                FROM delivery_orders 
                                WHERE delivery_order_id = {order_id})""")

    async def get_courier_location(self, courier_id):
        """Получаем id локации курьера"""
        return await self.pool.fetchval(
            f"""SELECT courier_location_id FROM couriers WHERE courier_id = {courier_id}"""
        )

    async def get_courier_name_by_id(self, courier_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(f"""
    select courier_name from couriers where courier_id={courier_id}""")

    async def get_couriers_for_location(self, location_id):
        """Получаем список курьеров, закрепленных за локацией"""
        return await self.pool.fetch(f"""
    SELECT courier_name, courier_telegram_id 
    FROM couriers 
    WHERE courier_location_id = {location_id} 
    AND courier_status = true""")

    async def get_courier_name(self, courier_tg_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(
            f"""SELECT courier_name FROM couriers WHERE courier_telegram_id = {courier_tg_id}""")

    ## couriers ##

    ## admins ##

    async def get_admin_id(self, user_id):
        """Получаем id админа"""
        return await self.pool.fetchval(f"""
    select admin_id 
    from admins 
    where admin_telegram_id={user_id}""")

    async def get_email_admin(self, user_id):
        """Получаем email админа локации"""
        return await self.pool.fetchval(f"""
    select admin_email 
    from admins 
    where admin_telegram_id = {user_id}""")

    async def get_admin_data(self, user_id):
        """Получаем инфу об админе локации"""
        return await self.pool.fetchval(f"""
    select admin_name 
    from admins 
    where admin_telegram_id = {user_id}""")

    async def get_delivery_admin_tg_id(self, order_id):
        """Получаем тг id админа"""
        return await self.pool.fetchval(f"""
    select admin_telegram_id 
    from admins
    where admin_id = (SELECT delivery_order_admin_id FROM delivery_orders WHERE delivery_order_id = {order_id})""")

    async def get_delivery_admin_telg_id(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchval(f"""
    SELECT admin_telegram_id 
    FROM admins 
    WHERE admin_id = (select delivery_order_admin_id from delivery_orders where delivery_order_id = {order_id})""")  ### del

    async def get_admins_list(self):
        """Получаем список админов"""
        return await self.pool.fetch(
            f"""SELECT admin_telegram_id from admins""")

    async def get_all_admin(self):
        """Получаем список админов"""
        return await self.pool.fetch("SELECT * FROM admins ORDER BY admin_id")

    ## admins ##

    ## delivery_category ##

    async def get_delivery_categories_with_products(self):
        """Получаем список доступных категорий"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT delivery_category_id, delivery_category_name 
    FROM delivery_categories
    JOIN delivery_products ON delivery_product_category_id = delivery_category_id
    order by delivery_category_id;"""
        )

    async def get_category_for_admin_delivery(self):
        """Выбираем все категории, в которых есть снятые с продажи товары"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT delivery_category_id, delivery_category_name 
    FROM delivery_categories
    JOIN delivery_products ON delivery_product_category_id=delivery_category_id
    WHERE is_de_product_available = false 
    ORDER BY delivery_category_id"""
        )

    async def get_delivery_category_for_remove_item_from_stock(self):
        """Выбираем все категории, в которых есть товары в продаже"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT  delivery_category_id, delivery_category_name 
    FROM  delivery_products
    JOIN delivery_categories ON delivery_product_category_id=delivery_category_id
    WHERE is_de_product_available = true ORDER BY delivery_category_id"""
        )

    async def get_list_of_delivery_categories_with_items(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""
    SELECT DISTINCT delivery_category_id, delivery_category_name
    FROM delivery_categories
    JOIN delivery_products on delivery_product_category_id = delivery_category_id
    ORDER BY delivery_category_id"""
        )  ### del

    async def get_delivery_category_list(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM delivery_categories 
    ORDER BY delivery_category_id"""
        )

    async def get_list_of_delivery_categories(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            """
    SELECT *
    FROM delivery_categories 
    ORDER BY delivery_category_id"""
        )  ### del

    async def get_delivery_categories(self):
        """Получаем список доступных категорий"""
        return await self.pool.fetch(f"""
    SELECT DISTINCT delivery_category_id, delivery_category_name 
    FROM delivery_categories
    JOIN delivery_products ON delivery_product_category_id = delivery_category_id
    WHERE is_de_category_available = true 
    AND is_de_product_available = true
    order by delivery_category_id;""")

    ## delivery_category ##

    ## delivery_orders ##

    async def get_unaccepted_delivery_orders(self):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Ожидание подтверждения'
    and delivery_order_admin_id is null
    and delivery_order_courier_id is null
    order by  delivery_order_datetime;""")

    async def get_delivery_orders_for_couriers(self, user_id):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Курьер не назначен'
    and delivery_order_admin_id = (select admin_id from admins where admin_telegram_id={user_id})
    and delivery_order_courier_id is null
    order by  delivery_order_datetime;""")

    async def get_delivery_orders_awaiting_delivery(self, user_id):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    join delivery_couriers on delivery_courier_id = delivery_order_courier_id
    where delivery_order_status = 'Заказ подтвержден'
    and delivery_order_admin_id = (select admin_id from admins where admin_telegram_id={user_id})
    and delivery_order_courier_id is not null
    order by  delivery_order_datetime;""")

    async def get_delivery_orders_awaiting_courier(self, user_id):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Ожидание подтверждения курьером'
    and delivery_order_admin_id = (select admin_id from admins where admin_telegram_id={user_id})
    order by  delivery_order_datetime;""")

    async def get_delivery_order_data(self, order_id):
        """Получаем информацию о заказе"""
        return await self.pool.fetchrow(
            f"""
    SELECT * 
    FROM delivery_orders 
    JOIN locations on delivery_order_location_id = location_id
    WHERE delivery_order_id = {order_id}"""
        )

    async def get_unaccepted_delivery_orders_ids(self):
        """Получаем список непринятых и измененных заказов"""
        return [order['delivery_order_id'] for order in await self.pool.fetch(f"""
    select delivery_order_id
    from delivery_orders
    where delivery_order_status = 'Ожидание подтверждения'""")]

    async def get_delivery_order_status(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchval(f"""
    SELECT delivery_order_status 
    FROM delivery_orders 
    WHERE delivery_order_id = {order_id}""")

    async def get_delivery_admin_id(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchrow(f"""
    SELECT delivery_order_admin_id, delivery_order_courier_id
    FROM delivery_orders 
    WHERE delivery_order_id = {order_id}""")

    async def get_delivery_order_owner(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchval(f"""
    SELECT admin_seller_telegram_id 
    FROM admin_sellers 
    WHERE admin_seller_id = (select delivery_order_seller_admin_id 
                            from delivery_orders 
                            where delivery_order_id = {order_id})""")

    async def get_first_delivery_order_date_admin(self):
        """Получаем первый день периода"""
        return await self.pool.fetchval(f"""
    select delivery_order_created_at
    from delivery_orders 
    order by delivery_order_id
    limit 1;""")

    async def get_delivery_orders_stat(self):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select location_name, delivery_order_id, delivery_order_seller_admin_id, delivery_order_admin_id, 
    delivery_order_courier_id, delivery_order_created_at, delivery_order_canceled_at, delivery_order_changed_at, 
    delivery_order_delivered_at, delivery_order_day_for_delivery, delivery_order_time_info, 
    delivery_order_final_price, delivery_order_status
    from delivery_orders 
    join locations on delivery_order_location_id = location_id
    order by delivery_order_id;""")]

    async def get_delivery_order_products_admin(self):
        return await self.pool.fetch(f"""
    select dop_order_id, dop_product_name, dop_quantity, dop_price_per_unit
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    order by  delivery_order_id;""")

    async def get_delivery_orders_count_admin(self):
        """"""
        return await self.pool.fetch(f"""
    select delivery_order_id, count(dop_order_id) as count
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    group by delivery_order_id
    order by delivery_order_id;""")

    async def get_delivery_indicators(self):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders""")

    async def get_admin_delivery_indicators_by_loc(self):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    join locations on delivery_order_location_id = location_id
    group by location_id, location_name
    order by location_id""")

    async def get_sellers_delivery_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_admin_id, admin_telegram_id, admin_name, 
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join admins on delivery_order_admin_id = admin_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    group by admin_telegram_id, delivery_order_admin_id, admin_name
    order by delivery_order_admin_id""")]

    async def get_couriers_delivery_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join delivery_couriers on delivery_order_courier_id = delivery_courier_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    group by delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name
    order by delivery_order_courier_id""")]

    async def get_users_delivery_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm

    from delivery_orders
    join admin_sellers on delivery_order_seller_admin_id = admin_seller_id
    join locations on admin_seller_location_id = location_id
    group by delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name
    order by delivery_order_seller_admin_id""")]

    async def get_delivery_orders_stat_by_date(self, first_day, last_day):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select location_name, delivery_order_id, delivery_order_seller_admin_id, delivery_order_admin_id, 
    delivery_order_courier_id, delivery_order_created_at, delivery_order_canceled_at, delivery_order_changed_at, 
    delivery_order_delivered_at, delivery_order_day_for_delivery, delivery_order_time_info, 
    delivery_order_final_price, delivery_order_status
    from delivery_orders 
    join locations on delivery_order_location_id = location_id
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    order by delivery_order_id;""")]

    async def get_delivery_order_products_admin_by_date(self, first_day, last_day):
        return await self.pool.fetch(f"""
    select dop_order_id, dop_product_name, dop_quantity, dop_price_per_unit
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    order by  delivery_order_id;""")

    async def get_delivery_orders_count_admin_by_date(self, first_day, last_day):
        """"""
        return await self.pool.fetch(f"""
    select delivery_order_id, count(dop_order_id) as count
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_id
    order by delivery_order_id;""")

    async def get_delivery_indicators_by_date(self, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price


    from delivery_orders
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'""")

    async def get_admin_delivery_indicators_by_loc_by_date(self, first_day, last_day):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by location_id, location_name
    order by location_id""")

    async def get_sellers_delivery_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_admin_id, admin_telegram_id, admin_name, 
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join admins on delivery_order_admin_id = admin_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by admin_telegram_id, delivery_order_admin_id, admin_name
    order by delivery_order_admin_id""")]

    async def get_couriers_delivery_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join delivery_couriers on delivery_order_courier_id = delivery_courier_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name
    order by delivery_order_courier_id""")]

    async def get_users_delivery_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm

    from delivery_orders
    join admin_sellers on delivery_order_seller_admin_id = admin_seller_id
    join locations on admin_seller_location_id = location_id
    where delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name
    order by delivery_order_seller_admin_id""")]

    async def get_delivery_orders_years(self):
        """Получаем годы"""
        return await self.pool.fetch(f"""
    select distinct extract(year from delivery_order_created_at) as delivery_year
    from delivery_orders 
    where delivery_order_created_at is not null
    order by delivery_year""")

    async def get_delivery_orders_months(self, year):
        """Получаем месяца"""
        return await self.pool.fetch(
            f"""
    select distinct extract(month from delivery_order_created_at)  as delivery_month
    from delivery_orders 
    where delivery_order_created_at is not null
    and extract(year from delivery_order_created_at) = '{year}'
    order by delivery_month""")

    async def get_delivery_orders_days(self, year, month):
        """Получаем месяца"""
        return await self.pool.fetch(f"""
    select distinct extract(day from delivery_order_created_at) as delivery_day
    from delivery_orders 
    where extract(year from delivery_order_created_at) = '{year}'
    and extract(month from delivery_order_created_at) = '{month}'
    order by delivery_day""")

    async def get_first_delivery_order_date_admin_by_loc(self, location_id):
        """Получаем первый день периода"""
        return await self.pool.fetchval(f"""
    select delivery_order_created_at
    from delivery_orders 
    where delivery_order_location_id = {location_id}
    order by delivery_order_id
    limit 1;""")

    async def get_delivery_orders_stat_by_loc(self, location_id):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select location_name, delivery_order_id, delivery_order_seller_admin_id, delivery_order_admin_id, 
    delivery_order_courier_id, delivery_order_created_at, delivery_order_canceled_at, delivery_order_changed_at, 
    delivery_order_delivered_at, delivery_order_day_for_delivery, delivery_order_time_info, 
    delivery_order_final_price, delivery_order_status
    from delivery_orders 
    join locations on delivery_order_location_id = location_id
    where delivery_order_location_id = {location_id}
    order by delivery_order_id;""")]

    async def get_delivery_orders_stat_by_loc_date(self, location_id, first_day, last_day):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select location_name, delivery_order_id, delivery_order_seller_admin_id, delivery_order_admin_id, 
    delivery_order_courier_id, delivery_order_created_at, 
    delivery_order_canceled_at, delivery_order_changed_at, delivery_order_delivered_at, 
    delivery_order_day_for_delivery, delivery_order_time_info, 
    delivery_order_final_price, delivery_order_status
    from delivery_orders 
    join locations on delivery_order_location_id = location_id
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    order by delivery_order_id;""")]

    async def get_delivery_order_products_admin_by_loc(self, location_id):
        return await self.pool.fetch(f"""
    select dop_order_id, dop_product_name, dop_quantity, dop_price_per_unit
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_location_id = {location_id}
    order by  delivery_order_id;""")

    async def get_delivery_order_products_admin_by_loc_date(self, location_id, first_day, last_day):
        return await self.pool.fetch(f"""
    select dop_order_id, dop_product_name, dop_quantity, dop_price_per_unit
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    order by  delivery_order_id;""")

    async def get_delivery_orders_count_admin_by_loc(self, location_id):
        """"""
        return await self.pool.fetch(f"""
    select delivery_order_id, count(dop_order_id) as count
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_location_id = {location_id}
    group by delivery_order_id
    order by delivery_order_id;""")

    async def get_delivery_orders_count_admin_by_loc_date(self, location_id, first_day, last_day):
        """"""
        return await self.pool.fetch(f"""
    select delivery_order_id, count(dop_order_id) as count
    from delivery_orders 
    join delivery_order_products on delivery_order_id = dop_order_id
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_id
    order by delivery_order_id;""")

    async def get_delivery_indicators_by_loc(self, location_id):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    where delivery_order_location_id = {location_id}""")

    async def get_delivery_indicators_by_loc_date(self, location_id, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'""")

    async def get_admin_delivery_indicators_by_loc_loc(self, location_id):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_location_id = {location_id}
    group by location_id, location_name
    order by location_id""")

    async def get_admin_delivery_indicators_by_loc_loc_date(self, location_id, first_day, last_day):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client,   
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings_price,

    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm,	
    SUM(delivery_order_final_price) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm_price,

    COUNT(*) as all_orders,
    SUM(delivery_order_final_price) as all_orders_price

    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by location_id, location_name
    order by location_id""")

    async def get_sellers_delivery_orders_admin_by_loc(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_admin_id, admin_telegram_id, admin_name, 
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join admins on delivery_order_admin_id = admin_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_location_id = {location_id}
    group by admin_telegram_id, delivery_order_admin_id, admin_name
    order by delivery_order_admin_id""")]

    async def get_sellers_delivery_orders_admin_by_loc_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_admin_id, admin_telegram_id, admin_name, 
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join admins on delivery_order_admin_id = admin_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by admin_telegram_id, delivery_order_admin_id, admin_name
    order by delivery_order_admin_id""")]

    async def get_couriers_delivery_orders_admin_by_loc(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join delivery_couriers on delivery_order_courier_id = delivery_courier_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_location_id = {location_id}
    group by delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name
    order by delivery_order_courier_id""")]

    async def get_couriers_delivery_orders_admin_by_loc_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings

    from delivery_orders
    join delivery_couriers on delivery_order_courier_id = delivery_courier_id
    where delivery_order_status in ('Заказ выполнен', 'Отменен поставщиком', 'Отменен клиентом', 'Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')
    and delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_courier_id, delivery_courier_telegram_id, delivery_courier_name
    order by delivery_order_courier_id""")]

    async def get_users_delivery_orders_admin_by_loc(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm

    from delivery_orders
    join admin_sellers on delivery_order_seller_admin_id = admin_seller_id
    join locations on admin_seller_location_id = location_id
    where delivery_order_location_id = {location_id}
    group by delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name
    order by delivery_order_seller_admin_id""")]

    async def get_users_delivery_orders_admin_by_loc_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name,
    count(*) as all_orders,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Заказ выполнен') as completed,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен поставщиком') as canceled_by_seller, 
    COUNT(*) FILTER (WHERE delivery_order_status = 'Отменен клиентом') as canceled_by_client, 
    COUNT(*) FILTER (WHERE delivery_order_status in ('Ожидание подтверждения курьером', 'Заказ подтвержден', 'Курьер не назначен')) as waitings,
    COUNT(*) FILTER (WHERE delivery_order_status = 'Ожидание подтверждения') as wait_confirm

    from delivery_orders
    join admin_sellers on delivery_order_seller_admin_id = admin_seller_id
    join locations on admin_seller_location_id = location_id
    where delivery_order_location_id = {location_id}
    and delivery_order_created_at >= '{first_day} 00:00:00'
    and delivery_order_created_at <= '{last_day} 23:59:59'
    group by delivery_order_seller_admin_id, admin_seller_telegram_id, admin_seller_name, location_name
    order by delivery_order_seller_admin_id""")]

    async def get_delivery_orders_years_by_loc(self, location_id):
        """Получаем годы"""
        return await self.pool.fetch(f"""
    select distinct extract(year from delivery_order_created_at) as delivery_year
    from delivery_orders 
    where delivery_order_created_at is not null
    and delivery_order_location_id = {location_id}
    order by delivery_year""")

    async def get_delivery_orders_months_by_loc(self, year, location_id):
        """Получаем месяца"""
        return await self.pool.fetch(
            f"""
    select distinct extract(month from delivery_order_created_at)  as delivery_month
    from delivery_orders 
    where delivery_order_created_at is not null
    and extract(year from delivery_order_created_at) = '{year}'
    and delivery_order_location_id = {location_id}
    order by delivery_month""")

    async def get_delivery_orders_days_by_loc(self, year, month, location_id):
        """Получаем месяцы"""
        return await self.pool.fetch(f"""
    select distinct extract(day from delivery_order_created_at) as delivery_day
    from delivery_orders 
    where extract(year from delivery_order_created_at) = '{year}'
    and extract(month from delivery_order_created_at) = '{month}'
    and delivery_order_location_id = {location_id}
    order by delivery_day""")

    async def get_accepted_delivery_orders_for_courier(self, courier_id):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Заказ подтвержден'
    and delivery_order_courier_id = (select delivery_courier_id
                                    from delivery_couriers
                                    where delivery_courier_telegram_id = {courier_id})       
    order by  delivery_order_datetime;""")

    async def get_accepted_delivery_orders_ids_for_courier(self, courier_id):
        """Получаем список непринятых и измененных заказов"""
        return [order['delivery_order_id'] for order in await self.pool.fetch(f"""
    select delivery_order_id
    from delivery_orders
    where delivery_order_status = 'Заказ подтвержден'
    and delivery_order_courier_id = (select delivery_courier_id
                                    from delivery_couriers
                                    where delivery_courier_telegram_id = {courier_id}) """)]

    async def get_unaccepted_delivery_orders_for_courier(self, courier_id):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select * 
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Ожидание подтверждения курьером'
    and delivery_order_courier_id = (select delivery_courier_id
                                    from delivery_couriers
                                    where delivery_courier_telegram_id = {courier_id})       
    order by  delivery_order_datetime;""")

    async def get_delivery_orders(self, user_id):
        """Получаем id последнего заказа"""
        return await self.pool.fetch(f"""
    SELECT * 
    FROM delivery_orders 
    WHERE delivery_order_seller_admin_id = (select admin_seller_id 
                                            from admin_sellers 
                                            where admin_seller_telegram_id = {user_id}) 
    AND delivery_order_status not in ('Отменен клиентом', 'Отменен поставщиком', 'Заказ выполнен')
    ORDER BY delivery_order_id""")

    async def get_delivery_products(self, category_id):
        """Получаем товары из категории"""
        return await self.pool.fetch(f"""
    SELECT delivery_product_id, delivery_product_name, delivery_price
    FROM delivery_products
    WHERE delivery_product_category_id = {category_id} 
    AND is_de_product_available = true
    ORDER BY delivery_product_id""")

    async def get_delivery_product_name_by_id(self, product_id):
        """Получаем название товара по id"""
        return await self.pool.fetchval(
            f"""SELECT delivery_product_name FROM delivery_products WHERE delivery_product_id = {product_id}""")

    async def get_delivery_order_id(self, user_id):
        """Получаем id последнего заказа"""
        return await self.pool.fetchval(f"""
    SELECT delivery_order_id 
    FROM delivery_orders 
    WHERE delivery_order_seller_admin_id = (select admin_seller_id 
                                            from admin_sellers 
                                            where admin_seller_telegram_id = {user_id}) 
    ORDER BY -delivery_order_id""")

    ## delivery_orders ##

    ## orders ##

    async def get_first_order_date_admin(self):
        """Получаем первый день периода"""
        return await self.pool.fetchval(f"""
    select order_date
    from orders 
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id
    limit 1;""")

    async def get_orders(self):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select order_id, order_user_id, order_seller_id, order_courier_id, order_date, order_created_at, order_accepted_at, 
    order_canceled_at, order_time_for_delivery, order_delivered_at, order_deliver_through,
    order_final_price, order_delivery_method, order_status, order_review, order_reason_for_rejection, local_object_name, 
    location_name
    from orders 
    join local_objects on local_object_id = order_local_object_id
    join locations on local_object_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")]

    async def get_orders_by_date(self, first_day, last_day):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select order_id, order_user_id, order_seller_id, order_courier_id, order_date, order_created_at, order_accepted_at, 
    order_canceled_at, order_time_for_delivery, order_delivered_at, order_deliver_through,
    order_final_price, order_delivery_method, order_status, order_review, order_reason_for_rejection, local_object_name, 
    location_name
    from orders 
    join local_objects on local_object_id = order_local_object_id
    join locations on local_object_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    order by order_id;""")]

    async def get_order_products_admin(self):
        return await self.pool.fetch(f"""
    select op_order_id, op_product_name, op_quantity, op_price_per_unit
    from orders 
    join order_products on order_id = op_order_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by  order_id;""")

    async def get_order_products_admin_by_date(self, first_day, last_day):
        return await self.pool.fetch(f"""
    select op_order_id, op_product_name, op_quantity, op_price_per_unit
    from orders 
    join order_products on order_id = op_order_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    order by  order_id;""")

    async def get_orders_count_admin(self):
        """"""
        return await self.pool.fetch(f"""
    select order_id, count(op_product_id) as count
    from orders 
    join order_products on order_id = op_order_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_id
    order by order_id;""")

    async def get_orders_count_admin_by_date(self, first_day, last_day):
        """"""
        return await self.pool.fetch(f"""
    select order_id, count(op_product_id) as count
    from orders 
    join order_products on order_id = op_order_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    group by order_id
    order by order_id;""")

    async def get_indicators(self):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')""")

    async def get_indicators_by_date(self, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'""")

    async def get_bonus_indicators_admin(self):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders

    from bonus_orders
    where  bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом');""")

    async def get_bonus_indicators_admin_by_date(self, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders

    from bonus_orders
    where  bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}';""")

    async def get_admin_indicators_by_loc(self):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    join local_objects on local_object_id = order_local_object_id
    join locations on local_object_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by location_id, location_name
    order by location_id""")

    async def get_admin_indicators_by_loc_date(self, first_day, last_day):
        return await self.pool.fetch(f"""
    select DISTINCT location_id, location_name,
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    join local_objects on local_object_id = order_local_object_id
    join locations on local_object_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    group by location_id, location_name
    order by location_id""")

    async def get_bonus_indicators_admin_by_loc(self):
        return await self.pool.fetch(f"""
    select DISTINCT location_name, location_id,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders

    from bonus_orders
    join locations on location_id = bonus_order_location_id
    where  bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    group by location_name, location_id
    order by location_id""")

    async def get_bonus_indicators_admin_by_loc_date(self, first_day, last_day):
        return await self.pool.fetch(f"""
    select DISTINCT location_name, location_id,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders

    from bonus_orders
    join locations on location_id = bonus_order_location_id
    where  bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    group by location_name, location_id
    order by location_id""")

    async def get_bonus_orders(self):
        """Получаем бонусные заказы"""
        return await self.pool.fetch(f"""
    select location_name, bonus_order_id, bonus_order_date, bonus_order_user_id, bonus_order_seller_id, 
    bonus_order_created_at, bonus_order_accepted_at, bonus_order_canceled_at, bonus_order_delivered_at, 
    bonus_order_quantity, bonus_order_status, bonus_order_review, bonus_order_reason_for_rejection
    from bonus_orders
    join locations on bonus_order_location_id = location_id
    where bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    order by bonus_order_id
        """)

    async def get_bonus_orders_by_date(self, first_day, last_day):
        """Получаем бонусные заказы"""
        return await self.pool.fetch(f"""
    select location_name, bonus_order_id, bonus_order_date, bonus_order_user_id, bonus_order_seller_id, 
    bonus_order_created_at, bonus_order_accepted_at, bonus_order_canceled_at, bonus_order_delivered_at, 
    bonus_order_quantity, bonus_order_status, bonus_order_review, bonus_order_reason_for_rejection
    from bonus_orders
    join locations on bonus_order_location_id = location_id
    where bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    order by bonus_order_id
        """)

    async def get_sellers_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_seller_id, seller_telegram_id, seller_name,  location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join sellers on order_seller_id = seller_id
    join locations on location_id = seller_location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by seller_telegram_id, order_seller_id, seller_name, location_name
    order by order_seller_id""")]

    async def get_sellers_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_seller_id, seller_telegram_id, seller_name,  location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join sellers on order_seller_id = seller_id
    join locations on location_id = seller_location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    group by seller_telegram_id, order_seller_id, seller_name, location_name
    order by order_seller_id""")]

    async def get_sellers_bonus_orders_admin(self):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_seller_id,  
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    where bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_seller_id
    order by bonus_order_seller_id""")

    async def get_sellers_bonus_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_seller_id,  
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    where bonus_order_status in ('Выдан', 'Отменен продавцом')
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    group by bonus_order_seller_id
    order by bonus_order_seller_id""")

    async def get_couriers_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_courier_id, courier_telegram_id, courier_name,  location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join couriers on order_courier_id = courier_id
    join locations on location_id = courier_location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_courier_id, courier_telegram_id, courier_name, location_name
    order by order_courier_id""")]

    async def get_couriers_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_courier_id, courier_telegram_id, courier_name,  location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join couriers on order_courier_id = courier_id
    join locations on location_id = courier_location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    group by order_courier_id, courier_telegram_id, courier_name, location_name
    order by order_courier_id""")]

    async def get_users_orders_admin(self):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_user_id, user_telegram_id, location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join users on order_user_id = user_id
    join locations on user_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_user_id, user_telegram_id, location_name
    order by order_user_id""")]

    async def get_users_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_user_id, user_telegram_id, location_name,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join users on order_user_id = user_id
    join locations on user_location_id = location_id
    where order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    group by order_user_id, user_telegram_id, location_name
    order by order_user_id""")]

    async def get_users_bonus_orders_admin(self):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_user_id, location_name,
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    join users on bonus_order_user_id = user_id
    join locations on user_location_id = location_id
    where bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_user_id, location_name
    order by bonus_order_user_id
    """)

    async def get_users_bonus_orders_admin_by_date(self, first_day, last_day):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_user_id, location_name,
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    join users on bonus_order_user_id = user_id
    join locations on user_location_id = location_id
    where bonus_order_status in ('Выдан', 'Отменен продавцом')
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    group by bonus_order_user_id, location_name
    order by bonus_order_user_id
    """)

    async def get_orders_years(self):
        """Получаем годы"""
        return await self.pool.fetch(f"""
    select distinct order_year 
    from orders 
    where order_year is not null
    order by order_year""")

    async def get_orders_months(self, year):
        """Получаем месяца"""
        return await self.pool.fetch(f"""
    select distinct order_month 
    from orders 
    where order_year = {year}
    and order_month is not null
    order by order_month""")

    async def get_orders_days(self, year, month):
        """Получаем месяца"""
        return await self.pool.fetch(f"""
    select distinct order_date 
    from orders 
    where order_year = {year}
    and order_month = {month}
    order by order_date""")

    async def get_last_order_id(self, user_id):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchval(
            f"""
    SELECT order_id 
    FROM orders 
    WHERE order_user_id = (select user_id from users where user_telegram_id = {user_id}) 
    ORDER BY -order_id"""
        )

    async def get_last_order_data(self, user_id):
        """Получаем данные текущего заказа"""
        return await self.pool.fetchrow(
            f"""
    SELECT order_id, local_object_name, location_id, order_final_price, order_address
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    JOIN locations on local_object_location_id=location_id
    WHERE order_user_id = (select user_id from users where user_telegram_id = {user_id})
    ORDER BY -order_id"""
        )

    async def get_order_pass_value(self, order_id):
        """Получаем статус способо доставки"""
        return await self.pool.fetchval(
            f"""
    SELECT order_pass_to_courier 
    FROM orders 
    WHERE order_id = {order_id}""")

    async def get_bonus_order_info(self, user_id):
        """Получаем инфу о последнем бонусном заказе"""
        return await self.pool.fetchrow(
            f"""
    SELECT *
    FROM bonus_orders 
    WHERE bonus_order_user_id = (select user_id from users where user_telegram_id={user_id})
    AND bonus_order_status = 'Ожидание продавца'
    ORDER BY -bonus_order_id""")

    async def get_bonus_order_status(self, b_order_id):
        """Получаем статус бонусного заказа"""
        return await self.pool.fetchval(
            f"""
    SELECT bonus_order_status 
    FROM bonus_orders 
    WHERE bonus_order_id = {b_order_id}""")

    async def can_cancel(self, order_id):
        """Получаем статус заказа"""
        status = await self.pool.fetchval(
            f"""
    SELECT order_status 
    FROM orders 
    WHERE order_id = {order_id}""")
        if status in ['Ожидание продавца', 'Принят', 'Приготовлен']:
            return True
        return False

    async def get_orders_for_user(self, user_id):
        """Получаем активные ордеры"""
        return await self.pool.fetch(
            f"""
    SELECT order_id, order_time_for_delivery, order_delivery_method, order_final_price, order_status
    FROM orders 
    WHERE order_user_id=(select user_id from users where user_telegram_id={user_id})
    AND order_status != 'Ожидание пользователя'
    AND order_status != 'Отклонен продавцом'
    AND order_status != 'Отменен пользователем'
    AND order_status != 'Отменен курьером'
    AND order_status != 'Выполнен'
    ORDER BY order_id"""
        )

    async def get_bonus_orders_for_user(self, user_id):
        """Получаем активные ордеры"""
        return await self.pool.fetch(
            f"""
    SELECT bonus_order_id, bonus_order_quantity, bonus_order_status
    FROM bonus_orders 
    WHERE bonus_order_user_id=(select user_id from users where user_telegram_id={user_id})
    AND bonus_order_status != 'Отменен пользователем до принятия продавцом'
    AND bonus_order_status != 'Отменен продавцом'
    AND bonus_order_status != 'Отклонен'
    AND bonus_order_status != 'Выдан'
    ORDER BY bonus_order_id"""
        )

    async def get_all_ready_orders_for_courier(self, courier_tg_id):
        """Получаем все заказы для курьера"""
        return await self.pool.fetch(
            f"""
    SELECT order_id, order_time_for_delivery, local_object_name, order_address, order_status, 
            order_final_price, user_telegram_id
    FROM orders 
    JOIN users on user_id=order_user_id
    JOIN local_objects on local_object_id=order_local_object_id
    WHERE order_courier_id = (select courier_id from couriers where courier_telegram_id = {courier_tg_id}) 
    AND order_status = 'Приготовлен'
    order by order_time_for_delivery""")

    async def get_all_waiting_orders_for_courier(self, courier_tg_id):
        """Получаем все заказы для курьера"""
        return await self.pool.fetch(f"""
    SELECT order_id, order_time_for_delivery, local_object_name, order_address, order_status, order_final_price
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    WHERE order_courier_id = (select courier_id from couriers where courier_telegram_id = {courier_tg_id}) 
    AND order_status = 'Принят'
    order by order_time_for_delivery""")

    async def order_is_not_canceled(self, order_id):
        """Проверяем не отменен ли заказ"""
        if await self.pool.fetchval(f"SELECT order_status FROM orders WHERE order_id ={order_id}") == 'Приготовлен':
            return True
        else:
            return False

    async def get_last_order_big_data(self, user_id):
        """Получаем данные текущего заказа"""
        return await self.pool.fetchrow(f"""
    SELECT order_id, local_object_name, location_id, order_final_price, order_address, order_delivery_method, 
            order_pass_to_courier, order_deliver_through, order_status
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    JOIN locations on local_object_location_id=location_id
    WHERE order_user_id = (select user_id from users where user_telegram_id = {user_id})
    ORDER BY -order_id""")

    async def get_last_order_location(self, user_id):
        """Получаем id локации и заказа"""
        return await self.pool.fetchrow(f"""
    SELECT order_id, location_id
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    JOIN locations on local_object_location_id=location_id
    WHERE order_user_id = (select user_id from users where user_telegram_id = {user_id})
    ORDER BY -order_id""")

    async def get_seller_courier(self, order_id):
        """Получаем id родавца и курьера"""
        return await self.pool.fetchrow(f"""
    select order_seller_id, order_courier_id
    from orders
    where order_id={order_id}""")

    async def get_temp_delivery_orders(self, user_id):
        """Получаем товары из 'Корзины' """
        return await self.pool.fetch(f"""
    SELECT * 
    FROM temp_delivery_orders 
    WHERE temp_delivery_order_user_telegram_id = {user_id}
    ORDER BY temp_delivery_order_id""")

    async def get_first_order_date(self, location_id):
        """Получаем первый день периода"""
        return await self.pool.fetchval(f"""
    select order_date
    from orders 
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")

    async def get_orders_by_location(self, location_id):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select order_id, order_user_id, order_seller_id, order_courier_id, order_date, order_created_at, order_accepted_at, 
    order_canceled_at, order_time_for_delivery, order_delivered_at, order_deliver_through, order_local_object_id, 
    order_final_price, order_delivery_method, order_status, order_review, order_reason_for_rejection, local_object_name
    from orders 
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")]

    async def get_orders_by_location_and_date(self, location_id, first_day, last_day):
        """"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select order_id, order_user_id, order_seller_id, order_courier_id, order_date, order_created_at, order_accepted_at, 
    order_canceled_at, order_time_for_delivery, order_delivered_at, order_deliver_through, order_local_object_id, 
    order_final_price, order_delivery_method, order_status, order_review, order_reason_for_rejection, local_object_name
    from orders 
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    order by order_id;""")]

    async def get_order_products_by_location(self, location_id):
        return await self.pool.fetch(f"""
    select op_order_id, op_product_name, op_quantity, op_price_per_unit
    from orders 
    join order_products on order_id = op_order_id
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")

    async def get_order_products_by_location_and_date(self, location_id, first_day, last_day):
        return await self.pool.fetch(f"""
    select op_order_id, op_product_name, op_quantity, op_price_per_unit
    from orders 
    join order_products on order_id = op_order_id
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")

    async def get_orders_count(self, location_id):
        """"""
        return await self.pool.fetch(f"""
    select order_id, count(op_product_id) as count
    from orders 
    join local_objects on local_object_id = order_local_object_id
    join order_products on order_id = op_order_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_id
    order by order_id;""")

    async def get_orders_count_by_location_and_date(self, location_id, first_day, last_day):
        """"""
        return await self.pool.fetch(f"""
    select order_id, count(op_product_id) as count
    from orders 
    join local_objects on local_object_id = order_local_object_id
    join order_products on order_id = op_order_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_id
    order by order_id;""")

    async def get_indicators_by_location(self, location_id):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')""")

    async def get_indicators_by_location_and_date(self, location_id, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE order_status = 'Выполнен') as completed,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Выполнен') as completed_price,

    COUNT(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier,   
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_price,

    COUNT(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client,	
    SUM(order_final_price) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_price,

    COUNT(*) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders,
    SUM(order_final_price) FILTER (WHERE order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')) as all_orders_price

    from orders
    join local_objects on local_object_id = order_local_object_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')""")

    async def get_bonus_indicators(self, location_id):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders
    from bonus_orders
    where  bonus_order_location_id = {location_id}
    and bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом');""")

    async def get_bonus_indicators_by_loc_and_date(self, location_id, first_day, last_day):
        return await self.pool.fetchrow(f"""
    select DISTINCT 
    COUNT(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_by_seller,
    COUNT(*) FILTER (WHERE bonus_order_status = 'Отменен пользователем до принятия продавцом') as canceled_by_client,
    COUNT(*) FILTER (WHERE bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')) as all_orders
    from bonus_orders
    where  bonus_order_location_id = {location_id}
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    and bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом');""")

    async def get_bonus_orders_by_location(self, location_id):
        """Получаем бонусные заказы"""
        return await self.pool.fetch(f"""
    select bonus_order_id, bonus_order_date, bonus_order_user_id, bonus_order_seller_id, bonus_order_created_at,
    bonus_order_accepted_at, bonus_order_canceled_at, bonus_order_delivered_at, bonus_order_quantity, 
    bonus_order_status, bonus_order_review, bonus_order_reason_for_rejection
    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    order by bonus_order_id""")

    async def get_bonus_orders_by_location_and_date(self, location_id, first_day, last_day):
        """Получаем бонусные заказы"""
        return await self.pool.fetch(f"""
    select bonus_order_id, bonus_order_date, bonus_order_user_id, bonus_order_seller_id, bonus_order_created_at,
    bonus_order_accepted_at, bonus_order_canceled_at, bonus_order_delivered_at, bonus_order_quantity, 
    bonus_order_status, bonus_order_review, bonus_order_reason_for_rejection
    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    and bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    order by bonus_order_id""")

    async def get_sellers_orders(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_seller_id, seller_telegram_id, seller_name,  
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join sellers on order_seller_id = seller_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by seller_telegram_id, order_seller_id, seller_name
    order by order_seller_id""")]

    async def get_sellers_orders_by_loc_and_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_seller_id, seller_telegram_id, seller_name,  
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join sellers on order_seller_id = seller_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by seller_telegram_id, order_seller_id, seller_name
    order by order_seller_id""")]

    async def get_sellers_bonus_orders(self, location_id):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_seller_id,  
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_seller_id
    order by bonus_order_seller_id""")

    async def get_sellers_bonus_orders_by_loc_and_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_seller_id,  
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    and bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_seller_id
    order by bonus_order_seller_id""")

    async def get_couriers_orders(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_courier_id, courier_telegram_id, courier_name,  
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join couriers on order_courier_id = courier_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_courier_id, courier_telegram_id, courier_name
    order by order_courier_id""")]

    async def get_couriers_orders_by_loc_and_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_courier_id, courier_telegram_id, courier_name,  
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join couriers on order_courier_id = courier_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_courier_id, courier_telegram_id, courier_name
    order by order_courier_id""")]

    async def get_users_orders(self, location_id):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_user_id, user_telegram_id,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join users on order_user_id = user_id
    where local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_user_id, user_telegram_id
    order by order_user_id""")]

    async def get_users_orders_by_loc_and_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return [dict(order) for order in await self.pool.fetch(f"""
    select distinct order_user_id, user_telegram_id,
    count(*) as all_orders,
    count(*) FILTER (WHERE order_status = 'Выполнен') as completed_orders,
    count(*) FILTER (WHERE order_status = 'Отклонен продавцом') as canceled_by_seller_orders,
    count(*) FILTER (WHERE order_status = 'Отменен пользователем') as canceled_by_client_orders,
    count(*) FILTER (WHERE order_status = 'Отменен курьером') as canceled_by_courier_orders

    from orders
    join local_objects on local_object_id = order_local_object_id
    join users on order_user_id = user_id
    where local_object_location_id = {location_id}
    and order_date >= '{first_day}'
    and order_date <= '{last_day}'
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    group by order_user_id, user_telegram_id
    order by order_user_id""")]

    async def get_users_bonus_orders(self, location_id):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_user_id,
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders


    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_user_id
    order by bonus_order_user_id""")

    async def get_users_bonus_orders_by_loc_and_date(self, location_id, first_day, last_day):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct bonus_order_user_id,
    count(*) as all_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Выдан') as completed_bonus_orders,
    count(*) FILTER (WHERE bonus_order_status = 'Отменен продавцом') as canceled_bonus_orders

    from bonus_orders
    where bonus_order_location_id = {location_id}
    and bonus_order_date >= '{first_day}'
    and bonus_order_date <= '{last_day}'
    and bonus_order_status in ('Выдан', 'Отменен продавцом')
    group by bonus_order_user_id
    order by bonus_order_user_id""")

    async def get_active_order_data(self, order_id):
        """Получаем данные текущего заказа"""
        return await self.pool.fetchrow(f"""
    SELECT local_object_name, order_final_price, order_address, order_time_for_delivery, courier_telegram_id
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    JOIN couriers on order_courier_id=courier_id
    WHERE order_id = {order_id}
    ORDER BY -order_id""")

    async def get_active_order_little_data(self, order_id):
        """получаем данные заказа"""
        return await self.pool.fetchrow(
            f"""select order_address, order_final_price from orders where order_id={order_id}""")

    async def get_unaccepted_bonus_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(f"""
    SELECT bonus_order_id, bonus_order_date, bonus_order_created_at, bonus_order_quantity
    FROM bonus_orders 
    WHERE bonus_order_location_id = {location_id}
    AND bonus_order_seller_id is null
    AND bonus_order_status = 'Ожидание продавца'
    order by bonus_order_id""")

    async def get_active_orders_by_seller(self, seller_id):
        """Получаем заказы"""
        return await self.pool.fetch(f"""
    SELECT order_id, order_delivery_method, order_time_for_delivery, order_courier_id, order_final_price, 
            user_telegram_id
    FROM orders 
    JOIN users on user_id=order_user_id
    WHERE order_seller_id = (select seller_id from sellers where seller_telegram_id={seller_id})
    AND order_status = 'Принят'
    order by order_id;""")

    async def get_unaccepted_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(f"""
    SELECT order_id, order_delivery_method, local_object_name, order_address, order_created_at, 
    order_date, order_deliver_through, order_pass_to_courier, order_final_price, order_status
    FROM orders 
    JOIN local_objects on local_object_id = order_local_object_id
    JOIN locations on local_object_location_id = location_id
    WHERE location_id = {location_id}
    AND order_seller_id is null
    AND order_status = 'Ожидание продавца'
    order by order_id""")

    async def get_delivery_orders_by_seller(self, seller_id):
        """Получаем заказы"""
        return await self.pool.fetch(f"""
    SELECT order_id, order_time_for_delivery, order_final_price, user_telegram_id, order_status
    FROM orders 
    Join users on user_id=order_user_id
    WHERE order_seller_id = (select seller_id from sellers where seller_telegram_id={seller_id})
    AND order_status = 'Приготовлен'
    AND order_delivery_method = 'Самовывоз'
    order by order_id;""")

    async def get_active_bonus_orders_by_seller_id(self, seller_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(f"""
    SELECT bonus_order_id, bonus_order_quantity, user_telegram_id
    FROM bonus_orders 
    join users on bonus_order_user_id=user_id
    WHERE bonus_order_seller_id = (select seller_id from sellers where seller_telegram_id={seller_id}) 
    AND bonus_order_status = 'Подтвержден, готовится'
    order by bonus_order_id""")

    async def get_ready_bonus_orders_by_seller_id(self, seller_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(f"""
    SELECT bonus_order_id, bonus_order_quantity, user_telegram_id
    FROM bonus_orders 
    join users on bonus_order_user_id=user_id
    WHERE bonus_order_seller_id = (select seller_id from sellers where seller_telegram_id={seller_id}) 
    AND bonus_order_status = 'Готов'
    order by bonus_order_id""")

    async def get_time_and_user_id(self, order_id):
        """Получаем время, за которое необходимо приготовить/доставить заказ"""
        return await self.pool.fetchrow(f"""
    SELECT order_deliver_through, user_telegram_id, location_id
    FROM orders 
    JOIN users on order_user_id=user_id
    JOIN local_objects on order_local_object_id=local_object_id
    JOIN locations ON local_object_location_id=location_id
    WHERE order_id = {order_id}""")

    async def get_order_data(self, order_id):
        """Получаем данные текущего заказа"""
        return await self.pool.fetchrow(f"""
    SELECT local_object_name, order_final_price, order_address, order_time_for_delivery, user_telegram_id
    FROM orders 
    JOIN local_objects on local_object_id=order_local_object_id
    JOIN users on order_user_id=user_id
    WHERE order_id = {order_id}
    ORDER BY -order_id""")

    async def get_order_products(self, order_id):
        """Получаем товары из заказа"""
        return await self.pool.fetch(f"""
    SELECT * FROM order_products WHERE op_order_id={order_id} order by op_order_id""")

    async def get_delivery_order_products(self, order_id):
        """Получаем товары из заказа"""
        return await self.pool.fetch(f"""
    SELECT * FROM delivery_order_products WHERE dop_order_id={order_id} order by dop_order_id""")

    async def get_count_products(self, category_id):
        """Получаем количество товаров в категории"""
        return await self.pool.fetchval(
            f"SELECT COUNT(*) from products where product_category_id={category_id}")

    async def get_count_products_delivery(self, category_id):
        """Получаем количество товаров в категории"""
        return await self.pool.fetchval(
            f"SELECT COUNT(*) from delivery_products where delivery_product_category_id={category_id}")

    ## orders ##

    ## temp_orders ##

    async def get_last_temp_order_id(self, user_id):
        """Получаем последний id товара"""
        return await self.pool.fetchrow(
            f"""
    select product_id, temp_order_id, size_id 
    from temp_orders 
    where temp_order_user_telegram_id = {user_id} 
    order by -temp_order_id"""
        )

    async def get_temp_orders(self, user_id):
        """Получаем товары из 'Корзины' """
        return await self.pool.fetch(
            f"""
    SELECT *
    FROM temp_orders 
    WHERE temp_order_user_telegram_id = {user_id} 
    ORDER BY temp_order_id"""
        )

    async def get_last_temp_order_only_id(self, user_id):
        return await self.pool.fetchval(f"""
    select temp_order_id 
    from temp_orders 
    where temp_order_user_telegram_id = {user_id} 
    order by -temp_order_id""")

    ## temp_orders ##

    async def get_about(self):
        """Получаем инфу о компании"""
        return await self.pool.fetchval(
            f"""
    SELECT info 
    FROM about""")

    ##### GET ########

    ##### UPDATE #####

    async def update_delivery_product_price(self, item_id, price):
        """Меняем цену"""
        await self.pool.execute(f"""
    UPDATE delivery_products 
    SET delivery_price = '{price}'
    WHERE delivery_product_id = {item_id}""")

    async def return_to_stock_delivery_item(self, product_id):
        """Возвращаем в продажу товар"""
        await self.pool.execute(
            f"""
    UPDATE delivery_products 
    SET is_de_product_available=true 
    WHERE delivery_product_id = {product_id}"""
        )

    async def remove_from_stock_delivery_item(self, product_id):
        """Убираем с продажи товар"""
        await self.pool.execute(
            f"""
    UPDATE delivery_products 
    SET is_de_product_available=false 
    WHERE delivery_product_id = {product_id}"""
        )

    async def ban_user(self, user_id, reason):
        """Блокируем пользователя"""
        await self.pool.execute(
            f"""
    UPDATE users 
    SET is_banned=true, reason_for_ban='{reason}'
    WHERE user_telegram_id={user_id}"""
        )

    async def unban_user(self, user_id):
        """Разблокируем пользователя"""
        await self.pool.execute(
            f"""
    UPDATE users 
    SET is_banned=false
    WHERE user_telegram_id={user_id}"""
        )

    async def reset_seller_admin_by_id(self, sa_id):
        """Сбрасываем админа локации"""
        await self.pool.execute(
            f"""
    UPDATE admin_sellers 
    SET admin_seller_metro_id=NULL, admin_seller_location_id=NULL
    WHERE admin_seller_id = {sa_id}"""
        )

    async def reset_seller_by_id(self, sa_id):
        """Сбрасываем продавца"""
        await self.pool.execute(
            f"""
    UPDATE sellers 
    SET seller_metro_id=NULL, seller_location_id=NULL
    WHERE seller_id = {sa_id}"""
        )

    async def reset_courier_by_id(self, sa_id):
        """Сбрасываем курьера"""
        await self.pool.execute(
            f"""
    UPDATE couriers 
    SET courier_metro_id=NULL, courier_location_id=NULL
    WHERE courier_id = {sa_id}"""
        )

    async def remove_from_stock_category(self, category_id):
        """Убираем с продажи категорию"""
        await self.pool.execute(
            f"""
    UPDATE categories 
    SET is_category_available=false 
    WHERE category_id = {category_id}"""
        )

    async def return_to_stock_category(self, category_id):
        """Возвращаем категорию в продажу"""
        await self.pool.execute(
            f"""
    UPDATE categories 
    SET is_category_available=true 
    WHERE category_id = {category_id}"""
        )

    async def remove_from_stock_item(self, product_id):
        """Убираем с продажи товар"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET is_product_available=false 
    WHERE product_id = {product_id}"""
        )

    async def return_to_stock_item(self, product_id):
        """Возвращаем в продажу товар"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET is_product_available=true 
    WHERE product_id = {product_id}"""
        )

    async def change_seller_admin_location(self, seller_admin_id, metro_id, location_id):
        """Меняем привязку к локации у продавца админа"""
        await self.pool.execute(
            f"""
    UPDATE admin_sellers 
    SET admin_seller_metro_id={metro_id}, admin_seller_location_id={location_id}
    WHERE admin_seller_id={seller_admin_id}"""
        )

    async def change_seller_location(self, seller_id, metro_id, location_id):
        """Меняем привязку к локации у продавца"""
        await self.pool.execute(
            f"""
    UPDATE sellers 
    SET seller_metro_id={metro_id}, seller_location_id={location_id}
    WHERE seller_id={seller_id}"""
        )

    async def change_courier_location(self, courier_id, metro_id, location_id):
        """Меняем привязку к локации у курьера"""
        await self.pool.execute(
            f"""
    UPDATE couriers 
    SET courier_metro_id={metro_id}, courier_location_id={location_id}
    WHERE courier_id={courier_id}"""
        )

    async def edit_metro_name(self, metro_id, metro_name):
        """Меняем название станции метро"""
        await self.pool.execute(
            f"""
    UPDATE metro 
    SET metro_name='{metro_name}' 
    WHERE metro_id={metro_id}"""
        )

    async def edit_product_name(self, product_id, product_name):
        """Обновляем название товара"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET product_name='{product_name}' 
    WHERE product_id={product_id}"""
        )

    async def edit_product_description(self, product_id, product_description):
        """Обновляем описание товара"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET product_description='{product_description}' 
    WHERE product_id={product_id}"""
        )

    async def edit_product_photo(self, product_id, product_photo_id):
        """Обновляем фотографию товара"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET product_photo_id='{product_photo_id}' 
    WHERE product_id={product_id}"""
        )

    async def edit_product_prices(self, product_id, prices):
        """Обновляем цены товара"""
        await self.pool.execute(
            f"""
    UPDATE products 
    SET price_1={prices['price1']}, price_2={prices['price2']}, price_3={prices['price3']},
    price_4={prices['price4']}, price_5={prices['price5']}, price_6={prices['price6']}
    WHERE product_id={product_id}"""
        )

    async def edit_size_name(self, size_id, size_name):
        """Меняем название размера"""
        await self.pool.execute(
            f"""
    UPDATE product_sizes 
    SET size_name='{size_name}' 
    WHERE size_id={size_id}"""
        )

    async def edit_size_prices(self, size_id, prices):
        """Меняем цены размера"""
        await self.pool.execute(
            f"""
    UPDATE product_sizes 
    SET price_1={prices['price1']}, price_2={prices['price2']}, price_3={prices['price3']}, price_4={prices['price4']}, 
        price_5={prices['price5']}, price_6={prices['price6']}
    WHERE size_id={size_id}"""
        )

    async def reset_delivery_order_admin(self, order_id):
        """Меняем статус"""
        await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_admin_id = null,
    delivery_order_status = 'Ожидание подтверждения'
    WHERE delivery_order_id = {order_id}""")

    async def update_delivery_order_admin(self, order_id, admin_id, status=None):
        """Меняем статус"""
        if status:
            await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_admin_id = {admin_id}, delivery_order_status = '{status}'
    WHERE delivery_order_id = {order_id}""")
        else:
            await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_admin_id = {admin_id}
    WHERE delivery_order_id = {order_id}""")

    async def update_delivery_order_courier_and_status(self, order_id, courier_id, status):
        """Меняем статус"""
        await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_courier_id = {courier_id}, delivery_order_status = '{status}'
    WHERE delivery_order_id = {order_id}""")

    async def update_delivery_order_status(self, order_id, status, cancel_time=None):
        """Меняем статус"""
        if cancel_time:
            await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_status = '{status}',
    delivery_order_canceled_at = now()
    WHERE delivery_order_id = {order_id}""")
        else:
            await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_status = '{status}'
    WHERE delivery_order_id = {order_id}""")

    async def update_email_admin(self, email, user_id):
        """Обновляем емайл"""
        await self.pool.execute(f"""
    UPDATE admins 
    SET admin_email='{email}'
    where admin_telegram_id = {user_id}""")

    async def change_bonus_minus(self, user_id, count_bonus):
        """Меняем количество бонусов"""
        bonus = await self.pool.fetchval(
            f"""
    SELECT bonus 
    FROM users 
    WHERE user_telegram_id = {user_id}"""
        )
        new_bonus = bonus - count_bonus
        await self.pool.execute(
            f"""
    UPDATE users 
    SET bonus = {new_bonus} 
    WHERE user_telegram_id = {user_id}"""
        )

    async def change_bonus_plus(self, user_id, count_bonus):
        """Меняем количество бонусов"""
        bonus = await self.pool.fetchval(
            f"""
    SELECT bonus 
    FROM users 
    WHERE user_telegram_id = {user_id}"""
        )
        new_bonus = bonus + count_bonus
        await self.pool.execute(
            f"""
    UPDATE users 
    SET bonus = {new_bonus} 
    WHERE user_telegram_id = {user_id}"""
        )

    async def set_bonus_order_status(self, order_id, status, reason=None):
        """Меняем статус бонусного заказа"""
        if reason:
            await self.pool.execute(
                f"""
    UPDATE bonus_orders 
    SET bonus_order_status = '{status}', bonus_order_reason_for_rejection = '{reason}'
    WHERE bonus_order_id = {order_id}""")
        else:
            await self.pool.execute(
                f"""
    UPDATE bonus_orders 
    SET bonus_order_status = '{status}'
    WHERE bonus_order_id = {order_id}""")

    async def set_bonus_order_canceled_at(self, bonus_order_id):
        """Устанавливаем время отмены заказа"""
        await self.pool.execute(
            f"""
    UPDATE bonus_orders 
    SET bonus_order_canceled_at = now()
    WHERE bonus_order_id = {bonus_order_id}""")

    async def set_bonus_order_delivered_at(self, bonus_order_id):
        """Устанавливаем время отмены заказа"""
        await self.pool.execute(
            f"""
    UPDATE bonus_orders 
    SET bonus_order_delivered_at = now()
    WHERE bonus_order_id = {bonus_order_id}""")

    async def set_bonus_order_taked(self, order_id):
        """Продавец принимает заказ"""
        await self.pool.execute(
            f"""
    UPDATE bonus_orders 
    SET bonus_order_status = 'Подтвержден, готовится', bonus_order_accepted_at = now()
    WHERE bonus_order_id = {order_id}""")

    async def im_at_work_courier(self, user_id, status):
        """Устанавливаем статус продавца"""
        await self.pool.execute(
            f"""
    UPDATE couriers 
    SET courier_status={status} 
    WHERE courier_telegram_id = {user_id}"""
        )

    async def update_order_status(self, order_id, order_status):
        """Обновляем статус заказа"""
        await self.pool.execute(
            f"""
    UPDATE orders 
    SET order_status = '{order_status}' 
    WHERE order_id = {order_id}"""
        )

    async def update_order_delivered_at(self, order_id):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_delivered_at = now() 
    WHERE order_id = {order_id}""")

    async def order_is_delivered(self, user_id):
        """Подтверждаем доставку/выдачу заказа"""
        num_user_and_inviter_id = await self.pool.fetchrow(f"""
    SELECT number_of_orders, inviter_id  
    FROM users 
    WHERE user_telegram_id = {user_id}""")
        num_orders = num_user_and_inviter_id['number_of_orders']
        try:
            inviter_id = int(num_user_and_inviter_id['inviter_id'])
        except Exception as err:
            logging.error(err)
            inviter_id = None
        if inviter_id:
            num_orders_and_bonus = await self.pool.fetchrow(f"""
    SELECT number_of_referral_orders, bonus  
    FROM users 
    WHERE user_telegram_id = {inviter_id}""")
            num_ref_orders = num_orders_and_bonus['number_of_referral_orders']
            bonus = num_orders_and_bonus['bonus']
            if num_orders == 0:
                bonus += 1
            num_orders += 1
            num_ref_orders += 1
            if num_ref_orders % 10 == 0:
                bonus += 1

            await self.pool.execute(f"""
    UPDATE users 
    SET number_of_orders = {num_orders} 
    WHERE user_telegram_id = {user_id}""")
            await self.pool.execute(f"""
    UPDATE users 
    SET number_of_referral_orders = {num_ref_orders}, bonus = {bonus}
    WHERE user_telegram_id = {inviter_id}""")
        else:
            num_orders += 1
            await self.pool.execute(f"""
    UPDATE users 
    SET number_of_orders = {num_orders} 
    WHERE user_telegram_id = {user_id}""")

    async def update_reason_for_rejection_courier(self, order_id, reason):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_reason_for_rejection = '{reason}', order_status = 'Отменен курьером', order_canceled_at = now()
    WHERE order_id = {order_id}""")

    async def update_delivery_order_courier_and_status_cancel(self, order_id):
        """Меняем статус"""
        await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_courier_id = null, delivery_order_status = 'Курьер не назначен'
    WHERE delivery_order_id = {order_id}""")

    async def update_delivery_order_delivered_at(self, order_id, status):
        """Меняем статус"""
        await self.pool.execute(f"""
    UPDATE delivery_orders 
    SET delivery_order_status = '{status}', delivery_order_delivered_at = now()
    WHERE delivery_order_id = {order_id}""")

    async def im_at_work_delivery_courier(self, user_id, status):
        """Устанавливаем статус продавца"""
        await self.pool.execute(f"""
    UPDATE delivery_couriers 
    SET delivery_courier_status={status} 
    WHERE delivery_courier_telegram_id = {user_id}""")

    async def update_quantity_and_price(self, order_id, product_price, quantity, order_price):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""
    UPDATE temp_orders 
    SET product_price = {product_price}, quantity = {quantity}, order_price = {order_price}
    WHERE temp_order_id = {order_id}"""
        await self.pool.execute(sql)

    async def update_quantity_size_and_price(self, order_id, product_price, quantity, order_price, size_id,
                                             product_name):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""
    UPDATE temp_orders 
    SET product_price = {product_price}, quantity = {quantity}, order_price = {order_price}, size_id = {size_id}, 
        product_name = '{product_name}'
    WHERE temp_order_id = {order_id}"""
        await self.pool.execute(sql)

    async def update_order_address(self, order_id, address):
        """Обновляем адрес доставки"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_address = '{address}' 
    WHERE order_id = {order_id}""")

    async def update_user_address(self, user_id, address):
        """Обновляем адрес доставки"""
        await self.pool.execute(f"""
    UPDATE users 
    SET user_address = '{address}' 
    WHERE user_telegram_id = {user_id}""")

    async def update_order_pass(self, order_id, pass_value):
        """Обновляем адрес доставки"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_pass_to_courier = '{pass_value}' 
    WHERE order_id = {order_id}""")

    async def update_order_deliver_through(self, order_id, time_value):
        """Обновляем время, для доставки"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_deliver_through = {time_value} 
    WHERE order_id = {order_id}""")

    async def update_order_status_and_date(self, order_id, date, time, status, year, month):
        """Обновляем статус и время создания заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_status = '{status}', order_date = '{date}', order_created_at = '{time}', order_year = {year},
        order_month = {month}
    WHERE order_id = {order_id}""")

    async def update_review(self, order_id, review):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_review = '{review}'
    WHERE order_id = {order_id}""")

    async def update_bonus_review(self, order_id, review):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE bonus_orders 
    SET bonus_order_review = '{review}'
    WHERE bonus_order_id = {order_id}""")

    async def update_user_info_without_address(self,
                                               user_id,
                                               user_metro_id,
                                               user_location_id,
                                               user_local_object_id
                                               ):
        """Обновляем информацию пользователя"""
        await self.pool.execute(f"""
    UPDATE users 
    SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id}, 
        user_local_object_id = {user_local_object_id}
    WHERE user_telegram_id = {user_id}""")

    async def cancel_delivery_order(self, order_id):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""
    UPDATE delivery_orders 
    SET delivery_order_status = 'Отменен клиентом', delivery_order_canceled_at = now()
    WHERE delivery_order_id = {order_id}"""
        await self.pool.execute(sql)

    async def update_delivery_order(self, order_id, changes, status):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""
    UPDATE delivery_orders 
    SET delivery_order_day_for_delivery = '{changes['new_delivery_date']}', 
    dlivery_order_time_for_delivery = '{changes['new_delivery_time']}', 
    delivery_order_datetime = '{changes['new_delivery_datetime']}',
    delivery_order_time_info = '{changes['choice']}', 
    delivery_order_changed_at = now(),
    delivery_order_status = '{status}'
    WHERE delivery_order_id = {order_id}"""
        await self.pool.execute(sql)

    async def remove_from_stock_category_in_location(self, category_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(
            f"""
    UPDATE locations_categories 
    SET is_category_in_location_available=false 
    WHERE lc_category_id = {category_id} 
    AND lc_location_id={location_id}""")

    async def return_from_stock_category_in_location(self, category_id, location_id):
        """Возвращем в продажу категорию в локации"""
        await self.pool.execute(f"""
    UPDATE locations_categories 
    SET is_category_in_location_available=true 
    WHERE lc_category_id = {category_id} 
    AND lc_location_id={location_id}""")

    async def remove_from_stock_product_in_location(self, product_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(f"""
    UPDATE locations_products 
    SET is_product_in_location_available=false 
    WHERE lp_product_id = {product_id} 
    AND lp_location_id={location_id}""")

    async def return_to_stock_product_in_location(self, product_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(f"""
    UPDATE locations_products 
    SET is_product_in_location_available=true 
    WHERE lp_product_id = {product_id} 
    AND lp_location_id={location_id}""")

    async def update_email(self, email, user_id):
        """Обновляем емайл"""
        await self.pool.execute(f"""
    UPDATE admin_sellers 
    SET admin_seller_email='{email}'
    where admin_seller_telegram_id = {user_id}""")

    async def update_reason_for_rejection(self, order_id, reason):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_reason_for_rejection = '{reason}', order_status = 'Отклонен продавцом', order_canceled_at = now()
    WHERE order_id = {order_id}""")

    async def take_bonus_order(self, order_id, new_seller_id):
        """Проверка и принятие заказа"""
        order_status = await self.pool.fetchval(
            f"SELECT bonus_order_status FROM bonus_orders WHERE bonus_order_id ={order_id}")
        bonus_seller_id = await self.pool.fetchval(
            f"SELECT bonus_order_seller_id FROM bonus_orders WHERE bonus_order_id ={order_id}")
        try:
            seller_id = await self.pool.fetchval(
                f"SELECT seller_id FROM sellers WHERE seller_telegram_id = {new_seller_id}")
        except:
            seller_id = None
        if bonus_seller_id == seller_id and order_status == 'Подтвержден, готовится' \
                or bonus_seller_id == seller_id and order_status == 'Готов':
            return True
        elif bonus_seller_id:
            return False
        elif order_status == 'Ожидание продавца':
            await self.pool.execute(f"""
    UPDATE bonus_orders 
    SET bonus_order_seller_id = (SELECT seller_id 
                                FROM sellers 
                                WHERE seller_telegram_id = {new_seller_id}) 
    WHERE bonus_order_id = {order_id}""")
            return True

    async def im_at_work_seller(self, user_id, status):
        """Устанавливаем статус продавца"""
        await self.pool.execute(
            f"""UPDATE sellers SET seller_status={status} WHERE seller_telegram_id = {user_id}""")

    async def take_order(self, order_id, user_id):
        """Обновляем статус заказа"""
        if await self.pool.fetchval(f"SELECT order_seller_id FROM orders WHERE order_id ={order_id}"):
            return False
        elif await self.pool.fetchval(
                f"SELECT order_status FROM orders WHERE order_id ={order_id}") == 'Ожидание продавца':
            await self.pool.execute(f"""
    UPDATE orders 
    SET order_seller_id = (SELECT seller_id FROM sellers WHERE seller_telegram_id = {user_id}) 
    WHERE order_id = {order_id}""")
            return True

    async def update_deliver_to(self, order_id, time_value, now_time):
        """Обновляем адрес доставки"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_time_for_delivery = '{time_value}', order_accepted_at = '{now_time}'
    WHERE order_id = {order_id}""")

    async def reset_order_time_and_seller(self, order_id):
        """Сброс продавца и времени"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_seller_id = null, order_time_for_delivery = null, order_courier_id = null,
        order_accepted_at = null
    WHERE order_id = {order_id}""")

    async def update_order_courier(self, order_id, courier_tg_id):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_courier_id = (select courier_id from couriers where courier_telegram_id={courier_tg_id})
    WHERE order_id = {order_id}""")

    ##### UPDATE #####

    ##### DELETE #####

    async def delete_delivery_product_by_id(self, product_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"""
    DELETE FROM delivery_products 
    WHERE delivery_product_id = {product_id}"""
        )

    async def delete_delivery_category_by_id(self, category_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"""
    DELETE FROM delivery_categories 
    WHERE delivery_category_id = {category_id}"""
        )

    async def delete_admin(self, admin_id):
        """Удаляем админа"""
        await self.pool.execute(
            f"""
    DELETE FROM admins 
    WHERE admin_id = {admin_id}"""
        )

    async def delete_metro(self, metro_id):
        """Удаляем метро"""
        await self.pool.execute(
            f"""
    DELETE FROM metro 
    WHERE metro_id = {metro_id}"""
        )

    async def delete_location_by_id(self, location_id):
        """Удаляем локацию"""
        await self.pool.execute(
            f"""
    DELETE FROM locations 
    WHERE location_id = {location_id}"""
        )

    async def delete_local_object_by_id(self, local_object_id):
        """Удаляем локацию"""
        await self.pool.execute(
            f"""
    DELETE FROM local_objects 
    WHERE local_object_id = {local_object_id}"""
        )

    async def delete_category_by_id(self, category_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"""
    DELETE FROM categories 
    WHERE category_id = {category_id}"""
        )

    async def delete_product_by_id(self, product_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"""
    DELETE FROM products 
    WHERE product_id = {product_id}"""
        )

    async def delete_seller_admin_by_id(self, sa_id):
        """Удаляем админа локации"""
        await self.pool.execute(
            f"""
    DELETE FROM admin_sellers 
    WHERE admin_seller_id = {sa_id}"""
        )

    async def delete_seller_by_id(self, seller_id):
        """Удаляем продавца"""
        await self.pool.execute(
            f"""
    DELETE FROM sellers 
    WHERE seller_id = {seller_id}"""
        )

    async def delete_courier_by_id(self, courier_id):
        """Удаляем курьера"""
        await self.pool.execute(
            f"""
    DELETE FROM couriers 
    WHERE courier_id = {courier_id}"""
        )

    async def delete_delivery_courier_by_id(self, courier_id):
        """Удаляем курьера"""
        await self.pool.execute(
            f"""
    DELETE FROM delivery_couriers 
    WHERE delivery_courier_id = {courier_id}"""
        )

    async def remove_size_by_id(self, size_id):
        """Удаляем размер"""
        await self.pool.execute(
            f"""
    DELETE FROM product_sizes 
    WHERE size_id = {size_id}"""
        )

    async def delete_from_cart(self, user_id):
        """Удаляем последний товар из корзины"""
        order_id = await self.pool.fetchval(
            f"""
    SELECT temp_order_id 
    FROM temp_orders 
    WHERE temp_order_user_telegram_id = {user_id} 
    ORDER BY -temp_order_id""")
        await self.pool.execute(
            f"""
    DELETE from temp_orders * 
    WHERE temp_order_user_telegram_id = {user_id}
    AND temp_order_id = {order_id}"""
        )

    async def delete_order_by_id(self, order_id):
        """Удаляем заказ"""
        await self.pool.execute(
            f"""
    DELETE FROM orders 
    WHERE order_id = {order_id}"""
        )

    async def clear_cart(self, user_id):
        """Очищаем корзину пользователя"""
        await self.pool.execute(
            f"""
    DELETE from temp_orders * 
    WHERE temp_order_user_telegram_id = {user_id}""")

    async def clear_empty_orders(self, user_id):
        """Очищаем корзину пользователя"""
        await self.pool.execute(
            f"""
    DELETE from orders * 
    WHERE order_user_id =(select user_id from users where user_telegram_id = {user_id}) 
    AND order_status = 'Ожидание пользователя'""")

    async def delete_temp_order_by_id(self, order_id):
        """Удаляем заказ"""
        await self.pool.execute(
            f"""
    DELETE FROM temp_orders 
    WHERE temp_order_id = {order_id}""")

    async def update_reason_for_rejection_user(self, order_id, reason):
        """Обновляем статус заказа"""
        await self.pool.execute(f"""
    UPDATE orders 
    SET order_reason_for_rejection = '{reason}', order_status = 'Отменен пользователем', order_canceled_at = now()
    WHERE order_id = {order_id}""")

    async def delete_last_temp_delivery_order_by_user(self, user_id):
        """Получаем id последнего заказа"""
        await self.pool.execute(f"""
    DELETE FROM temp_delivery_orders 
    WHERE temp_delivery_order_id = (SELECT temp_delivery_order_id 
                                    FROM temp_delivery_orders
                                    WHERE temp_delivery_order_user_telegram_id = {user_id} 
                                    ORDER BY - temp_delivery_order_id LIMIT 1)""")

    async def delete_temp_delivery_order_by_id(self, order_id):
        """Удаляем заказ"""
        await self.pool.execute(
            f"""DELETE FROM temp_delivery_orders WHERE temp_delivery_order_id = {order_id}"""
        )

    async def delete_temp_delivery_order_by_user_id(self, user_id):
        """Удаляем все заказы пользователя"""
        await self.pool.execute(
            f"""DELETE FROM temp_delivery_orders WHERE temp_delivery_order_user_telegram_id = {user_id}""")

    ##### DELETE #####

    ##### ADD ########

    async def add_delivery_category(self, category_name):
        """Добавляем категорию"""
        sql = """
    INSERT INTO delivery_categories (delivery_category_name) 
    VALUES ($1)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, category_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_delivery_item(self, item_data):
        """Добавляем товар"""
        sql = """
    INSERT INTO delivery_products (delivery_product_category_id, delivery_product_name, delivery_price) 
    VALUES ($1, $2, $3)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, item_data['category_id'],
                                        item_data['item_name'],
                                        item_data['price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def set_about(self, about):
        """Добавляем/изменяем инфу о компании"""
        await self.pool.execute(
            f"""
    DELETE FROM about"""
        )
        sql = """
    INSERT INTO about (info) 
    VALUES ($1)"""
        await self.pool.execute(sql, about)

    async def add_admin(self, admin_telegram_id, admin_name):
        """Добавляем админа"""
        sql = """
    INSERT INTO admins (admin_telegram_id, admin_name) 
    VALUES ($1, $2)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, admin_telegram_id, admin_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_metro(self, metro_name):
        """Добавляем метро"""
        sql = """
    INSERT INTO metro (metro_name) 
    VALUES ($1)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, metro_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_location(self, new_location):
        """Добавляем локацию"""
        sql = """
    INSERT INTO locations (location_name, location_address, location_metro_id) 
    VALUES ($1, $2, $3)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, new_location['location_name'], new_location['location_address'],
                                        new_location['metro_id'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        location_id = await self.pool.fetchval(
            """
    SELECT location_id 
    FROM locations 
    ORDER BY -location_id"""
        )
        category_ids = await self.pool.fetch(
            f"""
    SELECT category_id 
    FROM categories"""
        )
        for category in category_ids:
            sql_category = """
    INSERT INTO locations_categories (lc_location_id, lc_category_id) 
    VALUES ($1, $2)
                          """
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location_id, category['category_id'])
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1

        product_ids = await self.pool.fetch(
            f"""
    SELECT product_id 
    FROM products"""
        )
        for product in product_ids:
            sql_category = """
    INSERT INTO locations_products (lp_location_id, lp_product_id) 
    VALUES ($1, $2)
                          """
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location_id, product['product_id'])
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1
        product_size_ids = await self.pool.fetch(
            f"""
    SELECT size_id 
    FROM product_sizes"""
        )
        for size_id in product_size_ids:
            sql_category = """
    INSERT INTO locations_product_sizes (lps_location_id, lps_size_product_id) 
    VALUES ($1, $2)"""
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location_id, size_id['size_id'])
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1

    async def add_local_object(self, local_object_name, local_object_info):
        """Добавляем объект локальной доставки"""
        sql = """
    INSERT INTO local_objects (local_object_name, local_object_location_id, local_object_metro_id) 
    VALUES ($1, $2, $3)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, local_object_name, local_object_info['location_id'],
                                        local_object_info['metro_id'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_category(self, category_name):
        """Добавляем категорию"""
        sql = """
    INSERT INTO categories (category_name) 
    VALUES ($1)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, category_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        category_id = await self.pool.fetchval(
            f"""
    SELECT category_id 
    FROM categories 
    ORDER BY -category_id"""
        )
        location_ids = await self.pool.fetch(
            f"""
    SELECT location_id 
    FROM locations"""
        )
        for location in location_ids:
            sql_category = """
    INSERT INTO locations_categories (lc_location_id, lc_category_id) 
    VALUES ($1, $2)"""
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location['location_id'], category_id)
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1

    async def add_product_with_size(self, product_data):
        """Добавляем товар"""
        sql = """
    INSERT INTO products (product_category_id, product_name, product_description, product_photo_id) 
    VALUES ($1, $2, $3, $4)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, product_data['category_id'],
                                        product_data['item_name'],
                                        product_data['item_description'],
                                        product_data['photo_id'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        product_id = await self.pool.fetchval(
            f"""
    SELECT product_id 
    FROM products 
    ORDER BY -product_id"""
        )
        location_ids = await self.pool.fetch(
            f"""
    SELECT location_id 
    FROM locations"""
        )
        for location in location_ids:
            sql_category = """
    INSERT INTO locations_products (lp_location_id, lp_product_id) 
    VALUES ($1, $2)"""
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location['location_id'], product_id)
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1
        return product_id

    async def add_product_size(self, size_product_id, size_name, prices):
        """Добавляем размер товара товар"""
        sql = """
    INSERT INTO product_sizes (size_product_id, size_name, price_1, price_2, price_3, price_4, price_5, price_6) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, size_product_id,
                                        size_name,
                                        prices['price1'],
                                        prices['price2'],
                                        prices['price3'],
                                        prices['price4'],
                                        prices['price5'],
                                        prices['price6'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        size_id = await self.pool.fetchval(
            f"""
    SELECT size_id 
    FROM product_sizes 
    ORDER BY -size_id"""
        )
        location_ids = await self.pool.fetch(
            f"""
    SELECT location_id 
    FROM locations"""
        )
        for location in location_ids:
            sql_category = """
    INSERT INTO locations_product_sizes (lps_location_id, lps_size_product_id) 
    VALUES ($1, $2)
                                  """
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location['location_id'], size_id)
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1

    async def add_product(self, product_data):
        """Добавляем товар"""
        sql = """
    INSERT INTO products (product_category_id, product_name, product_description, product_photo_id,
                           price_1, price_2, price_3, price_4, price_5, price_6) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, product_data['category_id'],
                                        product_data['item_name'],
                                        product_data['item_description'],
                                        product_data['photo_id'],
                                        product_data['prices']['price1'],
                                        product_data['prices']['price2'],
                                        product_data['prices']['price3'],
                                        product_data['prices']['price4'],
                                        product_data['prices']['price5'],
                                        product_data['prices']['price6'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        product_id = await self.pool.fetchval(
            f"""
    SELECT product_id 
    FROM products 
    ORDER BY -product_id"""
        )
        location_ids = await self.pool.fetch(
            f"""
    SELECT location_id 
    FROM locations"""
        )
        for location in location_ids:
            sql_category = """
    INSERT INTO locations_products (lp_location_id, lp_product_id) 
    VALUES ($1, $2)
                                  """
            done_cat = False
            count_cat = 0
            while not done_cat:
                if count_cat == 15:
                    break
                try:
                    await self.pool.execute(sql_category, location['location_id'], product_id)
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count_cat == 14:
                        logging.error(err)
                    count_cat += 1

    async def add_seller_admin_without_location(self, admin_telegram_id, admin_name):
        """Добавляем админа без привязки к локации"""
        sql = """
    INSERT INTO admin_sellers (admin_seller_telegram_id, admin_seller_name) 
    VALUES ($1, $2)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, admin_telegram_id, admin_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_seller_admin(self, admin_telegram_id, admin_name, metro_id, location_id):
        """Добавляем админа с привязкой к локации"""
        sql = """
    INSERT INTO admin_sellers (admin_seller_telegram_id, admin_seller_name, admin_seller_metro_id, 
                               admin_seller_location_id) 
    VALUES ($1, $2, $3, $4)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, admin_telegram_id, admin_name, metro_id, location_id)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_seller_without_location(self, telegram_id, name):
        """Добавляем продавца без привязки к локации"""
        sql = """
    INSERT INTO sellers (seller_telegram_id, seller_name) 
    VALUES ($1, $2)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, telegram_id, name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_seller(self, telegram_id, name, metro_id, location_id):
        """Добавляем продавца с привязкой к локации"""
        sql = """
    INSERT INTO sellers (seller_telegram_id, seller_name, seller_metro_id, seller_location_id) 
    VALUES ($1, $2, $3, $4)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, telegram_id, name, metro_id, location_id)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_delivery_courier(self, delivery_courier_tg_id, courier_name):
        """Добавляем админа"""
        sql = """
    INSERT INTO delivery_couriers (delivery_courier_telegram_id, delivery_courier_name) 
    VALUES ($1, $2)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, delivery_courier_tg_id, courier_name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_courier_without_location(self, telegram_id, name):
        """Добавляем курьера без привязки к локации"""
        sql = """
    INSERT INTO couriers (courier_telegram_id, courier_name) 
    VALUES ($1, $2)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, telegram_id, name)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_courier(self, telegram_id, name, metro_id, location_id):
        """Добавляем курьера с привязкой к локации"""
        sql = """
    INSERT INTO couriers (courier_telegram_id, courier_name, courier_metro_id, courier_location_id) 
    VALUES ($1, $2, $3, $4)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, telegram_id, name, metro_id, location_id)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1
        return done

    async def add_bonus_order(self,
                              bonus_order_location_id,
                              bonus_order_date,
                              bonus_order_user_id,
                              bonus_order_created_at,
                              bonus_order_quantity,
                              bonus_order_status):
        """Формируем бунусный заказ"""
        sql = """
    INSERT INTO bonus_orders (bonus_order_location_id, bonus_order_date, bonus_order_user_id, 
                bonus_order_created_at, bonus_order_quantity, bonus_order_status) 
    VALUES ($1, $2, $3, $4, $5, $6)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, bonus_order_location_id, bonus_order_date, bonus_order_user_id,
                                        bonus_order_created_at, bonus_order_quantity, bonus_order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_user(self,
                       user_telegram_id: int,
                       user_metro_id,
                       user_location_id,
                       user_local_object_id):
        """Добавляем пользователя в таблицу"""
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_telegram_id})"):
            sql = """
    INSERT INTO users (user_telegram_id, user_metro_id, user_location_id, user_local_object_id) 
    VALUES ($1, $2, $3, $4)"""
            done = False
            count = 0
            while not done:
                if count == 15:
                    break
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count == 14:
                        logging.error(err)
                    count += 1
        else:
            await self.pool.execute(f"""
    UPDATE users 
    SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id}, 
        user_local_object_id = {user_local_object_id}""")
        return

    async def add_user_with_address(self,
                                    user_telegram_id: int,
                                    user_metro_id,
                                    user_location_id,
                                    user_local_object_id,
                                    address):
        """Добавляем пользователя в таблицу"""
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_telegram_id})"):
            sql = """
    INSERT INTO users (user_telegram_id, user_metro_id, user_location_id, user_local_object_id, user_address)
    VALUES ($1, $2, $3, $4, $5)"""
            done = False
            count = 0
            while not done:
                if count == 15:
                    break
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id, address)
                    done = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count == 14:
                        logging.error(err)
                    count += 1
        else:
            await self.pool.execute(f"""
    UPDATE users 
    SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id}, 
        user_local_object_id = {user_local_object_id}, user_address = {address}""")
        return

    async def add_temp_order(self, user_id, order_detail):
        """Добавляем временный ордер, чтобы потом сформировать список"""
        sql = """
    INSERT INTO temp_orders (temp_order_user_telegram_id, product_id, size_id, product_name, product_price,
                 quantity, order_price) 
    VALUES ($1, $2, $3, $4, $5, $6, $7)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, user_id, order_detail['product_id'], order_detail['size_id'],
                                        order_detail['product_name'], order_detail['product_price'],
                                        order_detail['quantity'], order_detail['order_price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_order_pickup(self,
                               order_user_id,
                               order_local_object_id,
                               order_address,
                               order_final_price,
                               order_delivery_method,
                               order_status):
        """Добавляем новый заказ в таблицу"""
        sql = """
    INSERT INTO orders (order_user_id, order_local_object_id, order_address, order_final_price, order_delivery_method, 
                order_status) 
    VALUES ($1, $2, $3, $4, $5, $6)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, order_user_id, order_local_object_id,
                                        order_address, order_final_price, order_delivery_method,
                                        order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_order(self,
                        order_user_id,
                        order_local_object_id,
                        order_final_price,
                        order_delivery_method,
                        order_status):
        """Добавляем новый заказ в таблицу"""
        sql = """
    INSERT INTO orders (order_user_id, order_local_object_id, order_final_price, order_delivery_method, order_status) 
    VALUES ($1, $2, $3, $4, $5)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, order_user_id, order_local_object_id,
                                        order_final_price, order_delivery_method, order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_order_product(self, op_order_id, order_detail):
        """Добавляем выбранные товары к заказу"""
        sql = """
    INSERT INTO order_products (op_order_id, op_product_id, op_size_id, op_product_name, op_quantity,
                op_price_per_unit, op_price) 
    VALUES ($1, $2, $3, $4, $5, $6, $7)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, op_order_id, order_detail['product_id'], order_detail['size_id'],
                                        order_detail['product_name'], order_detail['quantity'],
                                        order_detail['product_price'], order_detail['order_price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_temp_delivery_order(self, user_id, order_detail):
        """Добавляем временный ордер, чтобы потом сформировать список"""
        sql = """
    INSERT INTO temp_delivery_orders (temp_delivery_order_user_telegram_id, delivery_product_id, 
                delivery_product_name, delivery_product_price, delivery_quantity, delivery_order_price) 
    VALUES ($1, $2, $3, $4, $5, $6)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, user_id, order_detail['product_id'], order_detail['product_name'],
                                        order_detail['price'], order_detail['quantity'], order_detail['order_price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_delivery_order(self, user_id, order_data):
        """Добавляем новый заказ в таблицу"""
        seller_admin = await self.pool.fetchval(f"""select admin_seller_id from admin_sellers 
                                                    where admin_seller_telegram_id = {user_id}""")
        sql = """
    INSERT INTO delivery_orders (delivery_order_seller_admin_id, delivery_order_location_id, 
                delivery_order_day_for_delivery, dlivery_order_time_for_delivery, delivery_order_datetime, 
                delivery_order_time_info, delivery_order_final_price, delivery_order_status) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, seller_admin, order_data['location_id'], order_data['delivery_date'],
                                        order_data['delivery_time'], order_data['delivery_datetime'],
                                        order_data['choice'], order_data['final_price'], 'Ожидание подтверждения')
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_delivery_order_product(self, dop_order_id, order_detail):
        """Добавляем выбранные товары к заказу"""
        sql = """
        INSERT INTO delivery_order_products (dop_order_id, dop_product_id, dop_product_name, dop_quantity, 
                dop_price_per_unit, dop_price) 
        ALUES ($1, $2, $3, $4, $5, $6)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, dop_order_id, order_detail['delivery_product_id'],
                                        order_detail['delivery_product_name'], order_detail['delivery_quantity'],
                                        order_detail['delivery_product_price'], order_detail['delivery_order_price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def add_user_with_inviter(self,
                                    user_telegram_id: int,
                                    user_metro_id,
                                    user_location_id,
                                    user_local_object_id,
                                    inviter_id):
        """Добавляем пользователя в таблицу"""
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_telegram_id})"):
            sql = """
    INSERT INTO users (user_telegram_id, user_metro_id, user_location_id, user_local_object_id, inviter_id) 
    VALUES ($1, $2, $3, $4, $5)"""
            done = False
            count = 0
            while not done:
                if count == 15:
                    break
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id, inviter_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError as err:
                    if count == 14:
                        logging.error(err)
                    count += 1

        return

    async def add_referral(self, inviter_id):
        """Увеличиваем количиство рефералов"""
        ref_count = await self.pool.fetchval(
            f"SELECT number_of_referrals FROM users WHERE user_telegram_id = {inviter_id}")
        ref_count += 1
        await self.pool.execute(
            f"UPDATE users SET number_of_referrals = {ref_count} WHERE user_telegram_id = {inviter_id}")

    ##### ADD ########

    async def get_available_locations(self, metro_id):
        """Получаем список доступных локаций около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT location_id, location_name  FROM locations where location_metro_id = {metro_id} AND is_location_available = TRUE")

    async def get_location_data_by_id(self, location_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchrow(
            f"SELECT location_name, location_metro_id  FROM locations WHERE location_id = {location_id}"
        )

    async def get_local_object_name_by_id(self, local_object_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchval(
            f"SELECT local_object_name  FROM local_objects WHERE local_object_id = {local_object_id}"
        )

    async def get_user_adress_info(self, user_id):
        """Получаем инфу о пользователе для создания заказа"""
        return await self.pool.fetchrow(
            f"""SELECT user_metro_id, user_location_id, user_local_object_id, user_address
                FROM users WHERE user_telegram_id = {user_id}"""
        )

    async def get_last_user_order_detail_after_confirm(self, user_id):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchrow(
            f"""SELECT *
                FROM orders WHERE order_user_telegram_id = {user_id} ORDER BY -order_id"""
        )

    async def update_status(self, order_id, status):
        """Обновляем адрес доставки"""
        await self.pool.execute(
            f"""UPDATE orders SET order_status = '{status}' WHERE order_id = {order_id}"""
        )

    async def update_order_created_at(self, order_id):
        """Устанавливаем время заказа"""
        await self.pool.execute(
            f'UPDATE orders SET order_created_at = now() WHERE order_id = {order_id}'
        )

    async def get_product_category(self, product_id):
        """Получаем название товара"""
        return await self.pool.fetchval(
            f'SELECT product_category_id FROM products WHERE product_id = {product_id}'
        )

    async def get_location_address(self, location_id):
        """Достаем адрес локации"""
        return await self.pool.fetchval(
            f'SELECT location_address FROM locations WHERE location_id = {location_id}'
        )

    async def get_order_status(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchval(
            f'SELECT order_status FROM orders WHERE order_id = {order_id}'
        )

    async def get_order_info_for_courier(self, order_id):
        """Получаем информацию о заказе"""
        return await self.pool.fetchrow(
            f"""SELECT order_id, order_local_object_name, deliver_to, delivery_address, order_info, order_price,
                order_user_telegram_id
                FROM orders WHERE order_id = {order_id}"""
        )

    async def ready_order(self, order_id):
        """Обновляем статус заказа"""
        if await self.pool.fetchval(
                f"SELECT order_status FROM orders WHERE order_id = {order_id}") == "Подтвержден, готовится":
            await self.pool.execute(
                f"""UPDATE orders SET order_status = 'Заказ готов' WHERE order_id = {order_id}"""
            )
            return True
        else:
            return False

    async def get_ready_order_for_courier(self, order_id):
        """Получаем инфу о заказе для курьера"""
        return await self.pool.fetchrow(
            f"""
            SELECT deliver_to, order_info, order_local_object_name, order_courier_telegram_id, delivery_address,
            order_price
            FROM orders
            WHERE order_id = {order_id}
            """
        )

    async def get_all_ready_orders_for_sellers(self, location_id):
        """Получаем все заказы, готовые для выдачи"""
        return await self.pool.fetch(
            f"""
            SELECT order_id, deliver_to, order_info, order_status, order_price, order_user_telegram_id
            FROM orders
            WHERE order_location_id = {location_id} AND order_status = 'Заказ готов' AND delivery_method = 'Заберу сам'
            order by deliver_to
            """
        )

    async def update_user_info(self,
                               user_id,
                               user_metro_id,
                               user_location_id,
                               user_local_object_id,
                               user_address
                               ):
        """Обновляем информацию пользователя"""
        await self.pool.execute(
            f"""
            UPDATE users SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id},
            user_local_object_id = {user_local_object_id}, user_address = '{user_address}'
            WHERE user_telegram_id = {user_id}
            """
        )

    async def get_count_bonuses(self, user_id):
        """Получаем количество доступных бонусов"""
        return await self.pool.fetchval(
            f'SELECT bonus FROM users WHERE user_telegram_id = {user_id}'
        )

    async def get_location_address_by_user(self, user_id):
        """Достаем адес локации"""
        location_id = await self.pool.fetchval(
            f'SELECT user_location_id FROM users WHERE user_telegram_id = {user_id}'
        )
        return await self.pool.fetchval(
            f'SELECT location_address FROM locations WHERE location_id = {location_id}'
        )

    async def get_bonus_order_info_by_id(self, order_id):
        """Получаем инфу о последнем бонусном заказе"""
        return await self.pool.fetchrow(
            f"SELECT * FROM bonus_orders "
            f"WHERE bonus_order_id = {order_id}"
        )

    async def get_list_of_local_object(self):
        """Получаем список локаций"""
        return await self.pool.fetch(
            "SELECT * FROM local_objects ORDER BY location_id"
        )

    async def get_order_datetime(self, order_id):
        """Получаем дату и время доставки"""
        return await self.pool.fetchval(
            f"""SELECT delivery_datetime FROM delivery_orders WHERE delivery_order_id = {order_id}"""
        )

    async def get_accepted_delivery_orders(self):
        """Получаем список непринятых и измененных заказов"""
        return await self.pool.fetch(f"""
    select *
    from delivery_orders
    join locations on delivery_order_location_id = location_id
    where delivery_order_status = 'Заказ подтвержден'
    or  delivery_order_status = 'Заказ подтвержден после изменения'
    order by  delivery_order_datetime;""")

    async def get_accepted_delivery_orders_ids(self):
        """Получаем список непринятых и измененных заказов"""
        return [order['delivery_order_id'] for order in await self.pool.fetch(f"""
    select delivery_order_id
    from delivery_orders
    where delivery_order_status = 'Заказ подтвержден'""")]

    async def update_delivery_order_courier_null_and_status(self, order_id):
        """Меняем статус"""
        await self.pool.execute(f"""UPDATE delivery_orders
       SET delivery_order_courier_id = null,
       delivery_order_status = 'Ожидание подтверждения курьером'
       WHERE delivery_order_id = {order_id}""")

    async def get_orders_by_location_and_date_period(self, location_id, first_date, last_date):
        """"""
        return await self.pool.fetch(f"""
    select order_id, order_user_id, order_seller_id, order_courier_id, order_date, order_created_at, order_accepted_at,
    order_canceled_at, order_time_for_delivery, order_delivered_at, order_deliver_through, order_local_object_id,
    order_final_price, order_delivery_method, order_status, order_review, order_reason_for_rejection
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date >= '{first_date}'
	and order_date <= '{last_date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_id;""")

    async def get_bonus_orders_by_location_and_date_period(self, location_id, first_date, last_date):
        """Получаем бонусные заказы"""
        return await self.pool.fetch(f"""
    select bonus_order_id, bonus_order_date, bonus_order_user_id, bonus_order_seller_id, bonus_order_created_at,
    bonus_order_accepted_at, bonus_order_canceled_at, bonus_order_delivered_at, bonus_order_quantity, bonus_order_status,
    bonus_order_review, bonus_order_reason_for_rejection
    from bonus_orders
    where bonus_order_date >= '{first_date}'
	and bonus_order_date <= '{last_date}'
    and bonus_order_location_id = {location_id}
    and bonus_order_status in ('Выдан', 'Отменен продавцом', 'Отменен пользователем до принятия продавцом')
    order by bonus_order_id
    """)

    async def get_last_order_date(self, location_id):
        """Получаем первый день периода"""
        return await self.pool.fetchval(f"""
        select order_date
        from orders
        join local_objects on local_object_id = order_local_object_id
        where local_object_location_id = {location_id}
        and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
        order by -order_id;""")

    async def get_seller_ids_by_location_and_date(self, location_id, date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_seller_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date = '{date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_seller_id""")

    async def get_seller_ids_by_location_and_date_period(self, location_id, first_date, last_date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_seller_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date >= '{first_date}'
    and order_date <= '{last_date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_seller_id""")

    async def get_courier_ids_by_location(self, location_id):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
select distinct order_courier_id
from orders
join local_objects on local_object_id = order_local_object_id
where local_object_location_id = {location_id}
and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
and order_courier_id is not null
order by order_courier_id""")

    async def get_courier_ids_by_location_and_date(self, location_id, date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_courier_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date = '{date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_courier_id is not null
    order by order_courier_id""")

    async def get_courier_ids_by_location_and_date_period(self, location_id, first_date, last_date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_courier_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date >= '{first_date}'
    and order_date <= '{last_date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    and order_courier_id is not null
    order by order_courier_id""")

    async def get_clients_ids_by_location(self, location_id):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
select distinct order_user_id
from orders
join local_objects on local_object_id = order_local_object_id
where local_object_location_id = {location_id}
and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
order by order_user_id""")

    async def get_clients_ids_by_location_and_date(self, location_id, date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_user_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date = '{date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_user_id""")

    async def get_clients_ids_by_location_and_date_period(self, location_id, first_date, last_date):
        """Получаем id продавцов"""
        return await self.pool.fetch(f"""
    select distinct order_user_id
    from orders
    join local_objects on local_object_id = order_local_object_id
    where order_date >= '{first_date}'
    and order_date <= '{last_date}'
    and local_object_location_id = {location_id}
    and order_status in ('Выполнен', 'Отклонен продавцом', 'Отменен пользователем', 'Отменен курьером')
    order by order_user_id""")

    async def test_users(self):
        return await self.pool.fetch(
            "select user_id from users"
        )

    async def test_local(self):
        return await self.pool.fetch(
            "select local_object_id from local_objects where is_local_object_available = True"
        )

    async def test_sellers(self, local):
        return await self.pool.fetch(
            f"select seller_id from sellers where seller_status = True and seller_location_id = (select local_object_location_id from local_objects where local_object_id = {local})"
        )

    async def test_courier(self, local):
        return await self.pool.fetch(
            f"select courier_id from couriers where courier_status = True and courier_location_id = (select local_object_location_id from local_objects where local_object_id = {local})"
        )

    async def test_order(self,
                         order_year,
                         order_month,
                         order_user_id,
                         order_seller_id,
                         order_date,
                         order_created_at,
                         order_accepted_at,
                         order_time_for_delivery,
                         order_deliver_through,
                         order_local_object_id,
                         order_delivery_method,
                         order_status,
                         order_canceled_at=None,
                         order_delivered_at=None,
                         order_review=None,
                         order_reason_for_rejection=None,
                         order_courier_id=None):
        """Добавляем новый заказ в таблицу"""
        sql = """
        INSERT INTO orders (order_user_id, order_seller_id, order_courier_id, order_date,
        order_created_at, order_accepted_at, order_canceled_at, order_time_for_delivery,
        order_delivered_at, order_deliver_through, order_local_object_id,
        order_delivery_method, order_status, order_review, order_reason_for_rejection, order_year, order_month)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, order_user_id, order_seller_id, order_courier_id, order_date,
                                        order_created_at, order_accepted_at, order_canceled_at, order_time_for_delivery,
                                        order_delivered_at, order_deliver_through, order_local_object_id,
                                        order_delivery_method, order_status, order_review, order_reason_for_rejection,
                                        order_year, order_month)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def test_price(self, order_id, price):
        await self.pool.execute(f"""UPDATE orders SET order_final_price = {price} where order_id={order_id}""")

    async def test_products(self, quant):
        return await self.pool.fetch(f"""select * from products where is_product_available=True
LIMIT {quant}""")

    async def test_order_product(self, op_order_id, op_product_id, op_product_name, op_quantity,
                                 op_price_per_unit, op_price):
        """Добавляем выбранные товары к заказу"""
        sql = """
                INSERT INTO order_products (op_order_id, op_product_id, op_product_name, op_quantity,
                 op_price_per_unit, op_price)
                VALUES ($1, $2, $3, $4, $5, $6)
              """
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, op_order_id, op_product_id, op_product_name, op_quantity,
                                        op_price_per_unit, op_price)
                done = True
            except asyncpg.exceptions.UniqueViolationError as err:
                if count == 14:
                    logging.error(err)
                count += 1

    async def test_last_order(self):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchval(
            f'SELECT order_id FROM orders ORDER BY -order_id'
        )
