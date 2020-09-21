from datetime import datetime

import asyncpg
from asyncpg.pool import Pool

from data import config

now = datetime.now()


class Database:
    def __init__(self, pool):
        self.pool: Pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(
            user=config.PGUSER,
            database=config.PGDATABASE,
            password=config.PGPASSWORD,
            host="localhost",
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
           order_user_telegram_id INT NOT NULL,
           order_metro_id INT NOT NULL,
           order_location_id INT NOT NULL,
           order_local_object_id INT NOT NULL,
           order_local_object_name VARCHAR(255) NOT NULL,
           order_created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
           time_for_delivery INT,
           deliver_to TIME,
           delivery_method deliv_method,
           order_pass_for_courier VARCHAR(500),
           order_courier_name VARCHAR(255),
           order_courier_telegram_id INT,
           delivery_address TEXT,
           order_info TEXT,
           order_price INT,
           order_status or_status,
           reason_for_rejection TEXT
           );
           """
        try:
            await self.pool.execute("CREATE TYPE deliv_method AS ENUM ('С доставкой', 'Заберу сам');")
        except asyncpg.exceptions.DuplicateObjectError:
            print('Choices already exist')
        try:
            await self.pool.execute(
                "CREATE TYPE or_status AS ENUM ('Ожидание пользователя', 'Ожидание подтверждения продавца', 'Подтвержден, готовится', 'Отклонен', 'Заказ готов', 'Заказ доставлен/выдан');")
        except asyncpg.exceptions.DuplicateObjectError:
            print('Choices already exist')
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

    async def create_table_bonus_orders(self):
        """Создаем таблицу бонусных заказов"""
        sql = """
                   CREATE TABLE IF NOT EXISTS bonus_orders (
                   bonus_order_id SERIAL PRIMARY KEY,
                   bonus_order_user_telegram_id INT NOT NULL,
                   bonus_location_id INT NOT NULL,
                   bonus_quantity INT NOT NULL,
                   bonus_order_status VARCHAR(255)
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

    async def get_available_metro(self):
        """Получаем список доступных станций метро"""
        return await self.pool.fetch(
            """SELECT DISTINCT metro_id, metro_name  
FROM metro 
JOIN locations ON location_metro_id = metro_id
JOIN local_objects ON local_object_location_id = location_id
where is_metro_available = TRUE 
AND is_local_object_available = true ORDER BY metro_id""")

    async def get_metro_name_by_metro_id(self, metro_id):
        """Получаем название станции метро по его id"""
        return await self.pool.fetchval(f"SELECT metro_name FROM metro WHERE metro_id = {metro_id}")

    async def get_available_locations(self, metro_id):
        """Получаем список доступных локаций около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT location_id, location_name  FROM locations where location_metro_id = {metro_id} AND is_location_available = TRUE")

    async def get_locations_by_metro_id(self, metro_id):
        """Получаем список доступных локаций около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT location_id, location_name  FROM locations where location_metro_id = {metro_id}")

    async def get_available_local_objects(self, metro_id):
        """Получаем список доступных объектов доставки около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT local_object_id, local_object_name  FROM local_objects "
            f"where local_object_metro_id = {metro_id} AND is_local_object_available = TRUE")

    async def get_location_data_by_id(self, location_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchrow(
            f"SELECT location_name, location_metro_id  FROM locations WHERE location_id = {location_id}"
        )

    async def get_local_object_data_by_id(self, local_object_id):
        """Получаем информацию об объекте доставки по id"""
        return await self.pool.fetchrow(
            f"SELECT local_object_name, local_object_location_id, local_object_metro_id  FROM local_objects WHERE local_object_id = {local_object_id}"
        )

    async def get_location_name_by_id(self, location_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchval(
            f"SELECT location_name  FROM locations WHERE location_id = {location_id}"
        )

    async def get_local_object_name_by_id(self, local_object_id):
        """Получаем информацию о локации по id"""
        return await self.pool.fetchval(
            f"SELECT local_object_name  FROM local_objects WHERE local_object_id = {local_object_id}"
        )

    async def add_user(self,
                       user_telegram_id: int,
                       user_metro_id,
                       user_location_id,
                       user_local_object_id):
        """Добавляем пользователя в таблицу"""
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_telegram_id})"):
            sql = "INSERT INTO users (user_telegram_id, user_metro_id, user_location_id, user_local_object_id) VALUES ($1, $2, $3, $4)"
            done = False
            count = 0
            while not done:
                if count == 15:
                    break
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError:
                    count += 1
        else:
            await self.pool.execute(
                f"UPDATE users SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id},"
                f"user_local_object_id = {user_local_object_id}"
            )

        return

    async def add_user_with_inviter(self,
                                    user_telegram_id: int,
                                    user_metro_id,
                                    user_location_id,
                                    user_local_object_id,
                                    inviter_id):
        """Добавляем пользователя в таблицу"""
        if await self.pool.fetchval(
                f"SELECT NOT EXISTS(SELECT user_telegram_id FROM users WHERE user_telegram_id = {user_telegram_id})"):
            sql = "INSERT INTO users (user_telegram_id, user_metro_id, user_location_id, user_local_object_id, inviter_id) VALUES ($1, $2, $3, $4, $5)"
            done = False
            count = 0
            while not done:
                if count == 15:
                    break
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id, inviter_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError:
                    count += 1

        return

    async def add_referral(self, inviter_id):
        """Увеличиваем количиство рефералов"""
        ref_count = await self.pool.fetchval(
            f'SELECT number_of_referrals FROM users WHERE user_telegram_id = {inviter_id}'
        )
        ref_count += 1
        await self.pool.execute(
            f'UPDATE users SET number_of_referrals = {ref_count} WHERE user_telegram_id = {inviter_id}'
        )

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
        print(products_list)
        for prod in products_list:
            if prod['price_1']:
                prod_result.append(prod)
            else:
                with_size = await self.pool.fetchval(
                    f"""SELECT EXISTS(SELECT size_id FROM product_sizes 
                            WHERE size_product_id = {prod['product_id']})"""
                )
                print(with_size)
                if with_size:
                    prod_result.append(prod)
        return prod_result

    async def get_product_info_by_id(self, product_id, user_id):
        """Получаем подробную информацию о товаре"""
        sql = f"""
                        SELECT product_category_id, product_name, product_description, product_photo_id, price_1, 
                                price_2, price_3, price_4, price_5, price_6  
                        from products where product_id = {product_id};
                    """
        sql2 = f"""
                        SELECT product_sizes.size_id, product_sizes.size_name, product_sizes.price_1, product_sizes.size_product_id
                        FROM locations_product_sizes 
                        JOIN product_sizes ON locations_product_sizes.lps_size_product_id=product_sizes.size_id
                        WHERE product_sizes.size_product_id = {product_id}
        		        AND locations_product_sizes.lps_location_id = 
        		        (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
        		        AND product_sizes.is_size_available = true
        		        AND locations_product_sizes.is_size_product_in_location_available=true
        		        ORDER BY size_product_id;
                    """
        sql3 = f"""
                        SELECT product_category_id, product_name, product_description, product_photo_id 
                        from products where product_id = {product_id};
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

    async def add_temp_order(self, user_id, order_detail):
        """Добавляем временный ордер, чтобы потом сформировать список"""
        sql = """
                INSERT INTO temp_orders (temp_order_user_telegram_id, product_id, size_id, product_name, product_price,
                 quantity, order_price) 
                VALUES ($1, $2, $3, $4, $5, $6, $7)
              """
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def get_temp_orders(self, user_id):
        """Получаем товары из 'Корзины' """
        return await self.pool.fetch(
            f'SELECT * FROM temp_orders WHERE temp_order_user_telegram_id = {user_id} ORDER BY temp_order_id'
        )

    async def get_last_temp_order_id(self, user_id):
        """Получаем последний id товара"""
        return await self.pool.fetchrow(
            f'select product_id, temp_order_id, size_id from temp_orders where temp_order_user_telegram_id = {user_id} order by -temp_order_id'
        )

    async def get_last_temp_order_only_id(self, user_id):
        return await self.pool.fetchval(
            f'select temp_order_id from temp_orders where temp_order_user_telegram_id = {user_id} order by -temp_order_id'
        )

    async def update_quantity_and_price(self, order_id, product_price, quantity, order_price):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""UPDATE temp_orders SET product_price = {product_price}, quantity = {quantity}, order_price = {order_price}
            WHERE temp_order_id = {order_id}"""
        print(sql)
        await self.pool.execute(sql

                                )

    async def update_quantity_size_and_price(self, order_id, product_price, quantity, order_price, size_id,
                                             product_name):
        """Обновляем количество и цену после кнопки назад"""
        sql = f"""UPDATE temp_orders SET product_price = {product_price}, quantity = {quantity}, 
            order_price = {order_price}, size_id = {size_id}, product_name = '{product_name}'
            WHERE temp_order_id = {order_id}"""
        print(sql)
        await self.pool.execute(sql

                                )

    async def add_order(self,
                        order_user_telegram_id,
                        order_metro_id,
                        order_location_id,
                        order_local_object_id,
                        order_local_object_name,
                        delivery_method,
                        order_info,
                        order_price,
                        order_status):
        """Добавляем новый заказ в таблицу"""
        sql = """
        INSERT INTO orders (order_user_telegram_id, order_metro_id, order_location_id, order_local_object_id,
         order_local_object_name, delivery_method, order_info, order_price, order_status) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, order_user_telegram_id, order_metro_id, order_location_id,
                                        order_local_object_id,
                                        order_local_object_name, delivery_method, order_info, order_price, order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def add_order_pickup(self,
                               order_user_telegram_id,
                               order_metro_id,
                               order_location_id,
                               order_local_object_id,
                               order_local_object_name,
                               delivery_method,
                               delivery_address,
                               order_info,
                               order_price,
                               order_status):
        """Добавляем новый заказ в таблицу"""
        sql = """
        INSERT INTO orders (order_user_telegram_id, order_metro_id, order_location_id, order_local_object_id,
         order_local_object_name, delivery_method, delivery_address, order_info, order_price, order_status) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, order_user_telegram_id, order_metro_id, order_location_id,
                                        order_local_object_id, order_local_object_name, delivery_method,
                                        delivery_address, order_info, order_price, order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def get_user_address_data(self, user_id):
        """Получаем инфу о пользователе для создания заказа"""
        return await self.pool.fetchrow(
            f"""SELECT user_metro_id, user_location_id, user_local_object_id, user_address, location_address, 
                local_object_name
                FROM users 
                JOIN locations ON user_location_id=location_id
                JOIN local_objects ON local_object_id=user_local_object_id
                WHERE user_telegram_id = {user_id};"""
        )

    async def get_user_address_data_without_location_address(self, user_id):
        """Получаем инфу о пользователе для создания заказа"""
        return await self.pool.fetchrow(
            f"""SELECT user_metro_id, user_location_id, user_local_object_id, user_address, local_object_name
                FROM users 
                JOIN local_objects ON local_object_id=user_local_object_id
                WHERE user_telegram_id = {user_id};"""
        )

    async def get_user_adress_info(self, user_id):
        """Получаем инфу о пользователе для создания заказа"""
        return await self.pool.fetchrow(
            f"""SELECT user_metro_id, user_location_id, user_local_object_id, user_address
                FROM users WHERE user_telegram_id = {user_id}"""
        )

    async def get_last_order_id(self, user_id):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchval(
            f'SELECT order_id FROM orders WHERE order_user_telegram_id = {user_id} ORDER BY -order_id'
        )

    async def get_last_user_order_detail(self, user_id):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchrow(
            f"""SELECT order_id, order_local_object_name, order_location_id, deliver_to, delivery_address, order_info, 
                order_price, order_status, order_pass_for_courier, delivery_method
                FROM orders WHERE order_user_telegram_id = {user_id} ORDER BY -order_id"""
        )

    async def get_couriers_list(self, location_id):
        """Получаем список курьеров, закрепленных за локацией"""
        return await self.pool.fetch(
            f'SELECT courier_name FROM couriers WHERE courier_location_id = {location_id} AND courier_status = true'
        )

    async def update_order_address(self, order_id, address):
        """Обновляем адрес доставки"""
        await self.pool.execute(
            f"""UPDATE orders SET delivery_address = '{address}' WHERE order_id = {order_id}"""
        )

    async def update_user_address(self, user_id, address):
        """Обновляем адрес доставки"""
        await self.pool.execute(
            f"""UPDATE users SET user_address = '{address}' WHERE user_telegram_id = {user_id}"""
        )

    async def update_order_pass(self, order_id, pass_value):
        """Обновляем адрес доставки"""
        await self.pool.execute(
            f"""UPDATE orders SET order_pass_for_courier = '{pass_value}' WHERE order_id = {order_id}"""
        )

    async def update_deliver_to(self, order_id, time_value):
        """Обновляем адрес доставки"""
        await self.pool.execute(
            f"""UPDATE orders SET deliver_to = '{time_value}' WHERE order_id = {order_id}"""
        )

    async def get_last_user_order_detail_after_confirm(self, user_id):
        """Получаем id последнего заказа пользователя"""
        return await self.pool.fetchrow(
            f"""SELECT *
                FROM orders WHERE order_user_telegram_id = {user_id} ORDER BY -order_id"""
        )

    async def get_sellers_id_for_location(self, location_id):
        """Получаем доступных продавцов в локации"""
        return await self.pool.fetch(
            f'SELECT seller_telegram_id FROM sellers WHERE seller_location_id = {location_id} AND seller_status = true'
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

    async def update_order_status_and_created_at(self, order_id, status):
        """Обновляем статус и время создания заказа"""
        await self.pool.execute(
            f"""UPDATE orders SET order_status = '{status}', order_created_at = now() WHERE order_id = {order_id}"""
        )

    async def get_size_info(self, size_id):
        """Получаем информацию о размере"""
        return await self.pool.fetchrow(
            f'SELECT size_name, size_product_id, price_1, price_2, price_3, price_4, price_5, price_6 '
            f'from product_sizes where size_id = {size_id}'
        )

    async def get_product_name(self, product_id):
        """Получаем название товара"""
        return await self.pool.fetchval(
            f'SELECT product_name FROM products WHERE product_id = {product_id}'
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

    async def clear_cart(self, user_id):
        """Очищаем корзину пользователя"""
        await self.pool.execute(
            f'DELETE from temp_orders * WHERE temp_order_user_telegram_id = {user_id}'
        )

    async def delete_from_cart(self, user_id):
        """Удаляем последний товар из корзины"""
        order_id = await self.pool.fetchval(
            f'SELECT temp_order_id FROM temp_orders WHERE temp_order_user_telegram_id = {user_id} ORDER BY -temp_order_id'
        )
        await self.pool.execute(
            f"""DELETE from temp_orders * WHERE temp_order_user_telegram_id = {user_id}
                AND temp_order_id = {order_id}"""
        )

    async def clear_empty_orders(self, user_id):
        """Очищаем корзину пользователя"""
        await self.pool.execute(
            f"DELETE from orders * WHERE order_user_telegram_id = {user_id} AND order_status = 'Ожидание пользователя'"
        )

    async def update_time_for_delivery(self, order_id, time_value):
        """Обновляем время, для доставки"""
        await self.pool.execute(
            f"""UPDATE orders SET time_for_delivery = {time_value} WHERE order_id = {order_id}"""
        )

    async def get_order_pass_value(self, order_id):
        """Получаем статус способо доставки"""
        return await self.pool.fetchval(
            f"SELECT order_pass_for_courier FROM orders WHERE order_id = {order_id}"
        )

    async def get_time_and_user_id(self, order_id):
        """Получаем время, за которое необходимо приготовить/доставить заказ"""
        return await self.pool.fetchrow(
            f'SELECT time_for_delivery, order_user_telegram_id, order_location_id FROM orders WHERE order_id = {order_id}'
        )

    async def get_order_status(self, order_id):
        """Получаем статус заказа"""
        return await self.pool.fetchval(
            f'SELECT order_status FROM orders WHERE order_id = {order_id}'
        )

    async def get_user_tg_id(self, order_id):
        """Получаем id клиента"""
        return await self.pool.fetchval(
            f'SELECT order_user_telegram_id FROM orders WHERE order_id = {order_id}'
        )

    async def update_order_status(self, order_id, order_status):
        """Обновляем статус заказа"""
        await self.pool.execute(
            f"""UPDATE orders SET order_status = '{order_status}' WHERE order_id = {order_id}"""
        )

    async def update_reason_for_rejection(self, order_id, reason):
        """Обновляем статус заказа"""
        await self.pool.execute(
            f"""UPDATE orders SET reason_for_rejection = '{reason}' WHERE order_id = {order_id}"""
        )

    async def take_order(self, order_id):
        """Обновляем статус заказа"""
        if await self.pool.fetchval(
                f"SELECT order_status FROM orders WHERE order_id = {order_id}") == "Ожидание подтверждения продавца":
            await self.pool.execute(
                f"""UPDATE orders SET order_status = 'Подтвержден, готовится' WHERE order_id = {order_id}"""
            )
            return True
        else:
            return False

    async def get_couriers_for_location(self, location_id):
        """Получаем список курьеров, закрепленных за локацией"""
        return await self.pool.fetch(
            f'SELECT courier_name, courier_telegram_id FROM couriers WHERE courier_location_id = {location_id} AND courier_status = true'
        )

    async def get_courier_name(self, courier_tg_id):
        """Получаем имя курьера"""
        return await self.pool.fetchval(
            f'SELECT courier_name FROM couriers WHERE courier_telegram_id = {courier_tg_id}'
        )

    async def update_order_courier(self, order_id, courier_name, courier_tg_id):
        """Обновляем статус заказа"""
        await self.pool.execute(
            f"""UPDATE orders SET order_courier_name = '{courier_name}', order_courier_telegram_id = {courier_tg_id}
WHERE order_id = {order_id}"""
        )

    async def get_order_info_for_courier(self, order_id):
        """Получаем информацию о заказе"""
        return await self.pool.fetchrow(
            f"""SELECT order_id, order_local_object_name, deliver_to, delivery_address, order_info, order_price, 
                order_user_telegram_id 
                FROM orders WHERE order_id = {order_id}"""
        )

    async def get_seller_location_id(self, seller_id):
        """Получаем id локации продавца"""
        return await self.pool.fetchval(
            f'SELECT seller_location_id FROM sellers WHERE seller_telegram_id = {seller_id}'
        )

    async def get_active_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(
            f"""
            SELECT order_id, deliver_to, delivery_method, order_info, order_user_telegram_id
            FROM orders 
            WHERE order_location_id = {location_id} AND order_status = 'Подтвержден, готовится' order by deliver_to
            """
        )

    async def get_active_bonus_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(
            f"""
            SELECT *
            FROM bonus_orders 
            WHERE bonus_location_id = {location_id} AND bonus_order_status = 'Подтвержден, готовится'
            """
        )

    async def get_ready_bonus_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(
            f"""
            SELECT *
            FROM bonus_orders 
            WHERE bonus_location_id = {location_id} AND bonus_order_status = 'Готов'
            """
        )

    async def get_unaccepted_orders_by_location_id(self, location_id):
        """Получаем заказы для локации"""
        return await self.pool.fetch(
            f"""
            SELECT *
            FROM orders 
            WHERE order_location_id = {location_id} AND order_status = 'Ожидание подтверждения продавца' 
            order by order_created_at
            """
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

    async def get_all_ready_orders_for_courier(self, courier_tg_id):
        """Получаем все заказы для курьера"""
        return await self.pool.fetch(
            f"""
            SELECT order_id, deliver_to, order_info, order_local_object_name, 
            delivery_address, order_price, order_user_telegram_id
            FROM orders 
            WHERE order_courier_telegram_id = {courier_tg_id} AND order_status = 'Заказ готов'
            order by deliver_to
            """
        )

    async def get_all_waiting_orders_for_courier(self, courier_tg_id):
        """Получаем все заказы для курьера"""
        return await self.pool.fetch(
            f"""
            SELECT order_id, deliver_to, order_info, order_local_object_name, order_status,
            delivery_address, order_price
            FROM orders 
            WHERE order_courier_telegram_id = {courier_tg_id} AND order_status = 'Подтвержден, готовится'
            order by deliver_to
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

    async def order_is_delivered(self, order_id, user_id):
        """Подтверждаем доставку/выдачу заказа"""
        if await self.pool.fetchval(
                f'SELECT order_status FROM orders WHERE order_id = {order_id}'
        ) == 'Заказ готов':
            await self.pool.execute(
                f"UPDATE orders SET order_status = 'Заказ доставлен/выдан' WHERE order_id = {order_id}"
            )
            num_user_and_inviter_id = await self.pool.fetchrow(
                f"SELECT number_of_orders, inviter_id  FROM users WHERE user_telegram_id = {user_id}"
            )
            num_orders = num_user_and_inviter_id['number_of_orders']
            try:
                inviter_id = int(num_user_and_inviter_id['inviter_id'])
            except Exception as err:
                inviter_id = None
            print(inviter_id)
            if inviter_id:
                num_orders_and_bonus = await self.pool.fetchrow(
                    f"SELECT number_of_referral_orders, bonus  FROM users "
                    f"WHERE user_telegram_id = {inviter_id}"
                )
                num_ref_orders = num_orders_and_bonus['number_of_referral_orders']
                bonus = num_orders_and_bonus['bonus']
                print(bonus)
                print(num_ref_orders)
                if num_orders == 0:
                    bonus += 1
                num_orders += 1
                num_ref_orders += 1
                if num_ref_orders % 10 == 0:
                    bonus += 1
                print(bonus)
                print(num_ref_orders)
                print(num_orders)
                await self.pool.execute(
                    f'UPDATE users SET number_of_orders = {num_orders} WHERE user_telegram_id = {user_id}'
                )
                await self.pool.execute(
                    f'UPDATE users SET number_of_referral_orders = {num_ref_orders}, bonus = {bonus}'
                    f' WHERE user_telegram_id = {inviter_id}'
                )
            else:
                num_orders += 1
                print(num_orders)
                await self.pool.execute(
                    f'UPDATE users SET number_of_orders = {num_orders} WHERE user_telegram_id = {user_id}'
                )
            return True
        return False

    async def get_user(self, user_id):
        """Пытаемся получить пользователя из таблицы"""
        return await self.pool.fetchval(
            f'select user_telegram_id from users where user_telegram_id = {user_id}'
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

    async def update_user_info_without_address(self,
                                               user_id,
                                               user_metro_id,
                                               user_location_id,
                                               user_local_object_id
                                               ):
        """Обновляем информацию пользователя"""
        await self.pool.execute(
            f"""
            UPDATE users SET user_metro_id = {user_metro_id}, user_location_id = {user_location_id},
            user_local_object_id = {user_local_object_id}
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

    async def get_bonus_and_location_address(self, user_id):
        """Получаем количество бонусов и адес локации"""
        return await self.pool.fetchrow(
            f"""SELECT bonus, location_address
                FROM users 
                JOIN locations ON user_location_id=location_id
                WHERE user_telegram_id = {user_id};"""
        )

    async def get_user_location_id(self, user_id):
        """Получаем id локации пользователя"""
        return await self.pool.fetchval(
            f'SELECT user_location_id FROM users WHERE user_telegram_id = {user_id}'
        )

    async def add_bonus_order(self,
                              bonus_order_user_telegram_id,
                              bonus_location_id,
                              bonus_quantity,
                              bonus_order_status):
        """Формируем бунусный заказ"""
        sql = """
                INSERT INTO bonus_orders (bonus_order_user_telegram_id, bonus_location_id, bonus_quantity, 
                bonus_order_status) 
                VALUES ($1, $2, $3, $4)"""
        done = False
        count = 0
        while not done:
            if count == 15:
                break
            try:
                await self.pool.execute(sql, bonus_order_user_telegram_id, bonus_location_id, bonus_quantity,
                                        bonus_order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def get_bonus_order_info(self, user_id):
        """Получаем инфу о последнем бонусном заказе"""
        return await self.pool.fetchrow(
            f"SELECT * FROM bonus_orders "
            f"WHERE bonus_order_user_telegram_id = {user_id} AND bonus_order_status = 'Ожидание продавца'"
            f"ORDER BY -bonus_order_id"
        )

    async def get_bonus_order_info_by_id(self, order_id):
        """Получаем инфу о последнем бонусном заказе"""
        return await self.pool.fetchrow(
            f"SELECT * FROM bonus_orders "
            f"WHERE bonus_order_id = {order_id}"
        )

    async def set_bonus_order_status(self, order_id, status):
        """Меняем статус бонусного заказа"""
        await self.pool.execute(
            f"UPDATE bonus_orders SET bonus_order_status = '{status}' WHERE bonus_order_id = {order_id}"
        )

    async def change_bonus_minus(self, user_id, count_bonus):
        """Меняем количество бонусов"""
        bonus = await self.pool.fetchval(
            f'SELECT bonus FROM users WHERE user_telegram_id = {user_id}'
        )
        new_bonus = bonus - count_bonus
        await self.pool.execute(
            f'UPDATE users SET bonus = {new_bonus} WHERE user_telegram_id = {user_id}'
        )

    async def change_bonus_plus(self, user_id, count_bonus):
        """Меняем количество бонусов"""
        bonus = await self.pool.fetchval(
            f'SELECT bonus FROM users WHERE user_telegram_id = {user_id}'
        )
        new_bonus = bonus + count_bonus
        await self.pool.execute(
            f'UPDATE users SET bonus = {new_bonus} WHERE user_telegram_id = {user_id}'
        )

    async def get_bonus_order_status(self, b_order_id):
        """Получаем статус бонусного заказа"""
        return await self.pool.fetchval(
            f"SELECT bonus_order_status FROM bonus_orders WHERE bonus_order_id = {b_order_id}"
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        return done

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
            except asyncpg.exceptions.UniqueViolationError:
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
            except asyncpg.exceptions.UniqueViolationError:
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
            except asyncpg.exceptions.UniqueViolationError:
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        return done

    async def add_seller(self, telegram_id, name, metro_id, location_id):
        """Добавляем продавца с привязкой к локации"""
        sql = """
                INSERT INTO sellers (seller_telegram_id, seller_name, seller_metro_id, 
                seller_location_id) 
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        return done

    async def add_courier(self, telegram_id, name, metro_id, location_id):
        """Добавляем курьера с привязкой к локации"""
        sql = """
                INSERT INTO couriers (courier_telegram_id, courier_name, courier_metro_id, 
                courier_location_id) 
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        return done

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

    async def get_all_admin(self):
        """Получаем список админов"""
        return await self.pool.fetch(
            "SELECT * FROM admins ORDER BY admin_id"
        )

    async def delete_admin(self, admin_id):
        """Удаляем админа"""
        await self.pool.execute(
            f"DELETE FROM admins WHERE admin_id = {admin_id}"
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def get_all_metro(self):
        """Получаем список метро"""
        return await self.pool.fetch(
            "SELECT * FROM metro ORDER BY metro_id"
        )

    async def get_last_metro_id(self):
        """Получаем id последней добавленной ветки метро"""
        return await self.pool.fetchval(
            "SELECT metro_id FROM metro ORDER BY -metro_id"
        )

    async def get_metro_name_by_id(self, metro_id):
        """Получаем название ветки метро по id"""
        return await self.pool.fetchval(
            f"SELECT metro_name FROM metro WHERE metro_id = {metro_id}"
        )

    async def delete_metro(self, metro_id):
        """Удаляем метро"""
        await self.pool.execute(
            f"DELETE FROM metro WHERE metro_id = {metro_id}"
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        location_id = await self.pool.fetchval(
            "SELECT location_id FROM locations ORDER BY -location_id"
        )
        print(location_id)
        category_ids = await self.pool.fetch(
            f"SELECT category_id FROM categories"
        )
        print(category_ids)
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
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1

        product_ids = await self.pool.fetch(
            f"SELECT product_id FROM products"
        )
        print(product_ids)
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
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1
        product_size_ids = await self.pool.fetch(
            f"SELECT size_id FROM product_sizes"
        )
        print(product_size_ids)
        for size_id in product_size_ids:
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
                    await self.pool.execute(sql_category, location_id, size_id['size_id'])
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1

    async def get_list_of_locations(self):
        """Получаем список локаций"""
        return await self.pool.fetch(
            "SELECT * FROM local_objects ORDER BY local_object_id"
        )

    async def get_list_of_categories(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            "SELECT * FROM categories ORDER BY category_id"
        )

    async def get_list_of_local_object(self):
        """Получаем список локаций"""
        return await self.pool.fetch(
            "SELECT * FROM locations ORDER BY location_id"
        )

    async def get_metro_name_by_location_metro_id(self, location_metro_id):
        """Получаем название ветки метро"""
        return await self.pool.fetchval(
            f"SELECT metro_name FROM metro WHERE metro_id = {location_metro_id}"
        )

    async def delete_location_by_id(self, location_id):
        """Удаляем локацию"""
        await self.pool.execute(
            f"DELETE FROM locations WHERE location_id = {location_id}"
        )

    async def delete_local_object_by_id(self, local_object_id):
        """Удаляем локацию"""
        await self.pool.execute(
            f"DELETE FROM local_objects WHERE local_object_id = {local_object_id}"
        )

    async def delete_category_by_id(self, category_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"DELETE FROM categories WHERE category_id = {category_id}"
        )

    async def delete_seller_admin_by_id(self, sa_id):
        """Удаляем админа локации"""
        await self.pool.execute(
            f"DELETE FROM admin_sellers WHERE admin_seller_id = {sa_id}"
        )

    async def reset_seller_admin_by_id(self, sa_id):
        """Сбрасываем админа локации"""
        await self.pool.execute(
            f"""UPDATE admin_sellers SET admin_seller_metro_id=NULL, admin_seller_location_id=NULL
WHERE admin_seller_id = {sa_id}"""
        )

    async def reset_seller_by_id(self, sa_id):
        """Сбрасываем продавца"""
        await self.pool.execute(
            f"""UPDATE sellers SET seller_metro_id=NULL, seller_location_id=NULL
    WHERE seller_id = {sa_id}"""
        )

    async def reset_courier_by_id(self, sa_id):
        """Сбрасываем курьера"""
        await self.pool.execute(
            f"""UPDATE couriers SET courier_metro_id=NULL, courier_location_id=NULL
    WHERE courier_id = {sa_id}"""
        )

    async def delete_seller_by_id(self, seller_id):
        """Удаляем продавца"""
        await self.pool.execute(
            f"DELETE FROM sellers WHERE seller_id = {seller_id}"
        )

    async def delete_courier_by_id(self, courier_id):
        """Удаляем курьера"""
        await self.pool.execute(
            f"DELETE FROM couriers WHERE courier_id = {courier_id}"
        )

    async def delete_product_by_id(self, product_id):
        """Удаляем категорию"""
        await self.pool.execute(
            f"DELETE FROM products WHERE product_id = {product_id}"
        )

    async def remove_from_stock_category(self, category_id):
        """Убираем с продажи категорию"""
        await self.pool.execute(
            f"""UPDATE categories SET is_category_available=false WHERE category_id = {category_id}"""
        )

    async def remove_from_stock_category_in_location(self, category_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(
            f"""UPDATE locations_categories SET is_category_in_location_available=false 
WHERE lc_category_id = {category_id} AND lc_location_id={location_id}"""
        )

    async def return_from_stock_category_in_location(self, category_id, location_id):
        """Возвращем в продажу категорию в локации"""
        await self.pool.execute(
            f"""UPDATE locations_categories SET is_category_in_location_available=true 
    WHERE lc_category_id = {category_id} AND lc_location_id={location_id}"""
        )

    async def remove_from_stock_product_in_location(self, product_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(
            f"""UPDATE locations_products SET is_product_in_location_available=false 
    WHERE lp_product_id = {product_id} AND lp_location_id={location_id}"""
        )

    async def return_to_stock_product_in_location(self, product_id, location_id):
        """Убираем с продажи категорию в локации"""
        await self.pool.execute(
            f"""UPDATE locations_products SET is_product_in_location_available=true 
    WHERE lp_product_id = {product_id} AND lp_location_id={location_id}"""
        )

    async def return_to_stock_category(self, category_id):
        """Возвращаем категорию в продажу"""
        await self.pool.execute(
            f"""UPDATE categories SET is_category_available=true WHERE category_id = {category_id}"""
        )

    async def remove_from_stock_item(self, product_id):
        """Убираем с продажи товар"""
        await self.pool.execute(
            f"""UPDATE products SET is_product_available=false WHERE product_id = {product_id}"""
        )

    async def return_to_stock_item(self, product_id):
        """Возвращаем в продажу товар"""
        await self.pool.execute(
            f"""UPDATE products SET is_product_available=true WHERE product_id = {product_id}"""
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1

    async def get_local_objects_list(self):
        """Получаем список объектов доставки"""
        return await self.pool.fetch(
            f"""SELECT * 
FROM local_objects 
JOIN locations ON locations.location_id = local_objects.local_object_location_id
ORDER BY local_object_location_id
"""
        )

    async def get_category_list(self):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""SELECT * FROM categories ORDER BY category_id"""
        )

    async def get_seller_admins_list(self):
        """Получаем список админов локаций"""
        return await self.pool.fetch(
            f"""SELECT * FROM admin_sellers ORDER BY admin_seller_id"""
        )

    async def get_seller_list(self):
        """Получаем список Продавцов локаций"""
        return await self.pool.fetch(
            f"""SELECT * FROM sellers ORDER BY seller_id"""
        )

    async def get_courier_list(self):
        """Получаем список Продавцов локаций"""
        return await self.pool.fetch(
            f"""SELECT * FROM couriers ORDER BY courier_id"""
        )

    async def get_products_list(self, category_id):
        """Получаем список категорий"""
        return await self.pool.fetch(
            f"""SELECT product_id, product_name FROM products  WHERE product_category_id={category_id}
ORDER BY product_id"""
        )

    async def get_count_products(self, category_id):
        """Получаем количество товаров в категории"""
        return await self.pool.fetchval(
            f"SELECT COUNT(*) from products where product_category_id={category_id}"
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        category_id = await self.pool.fetchval(
            f"SELECT category_id FROM categories ORDER BY -category_id"
        )
        location_ids = await self.pool.fetch(
            f"SELECT location_id FROM locations"
        )
        for location in location_ids:
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
                    await self.pool.execute(sql_category, location['location_id'], category_id)
                    done_cat = True
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1

    async def get_category_name_by_id(self, category_id):
        """Получааем название категории"""
        return await self.pool.fetchval(
            f"SELECT category_name FROM categories WHERE category_id = {category_id}"
        )

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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        product_id = await self.pool.fetchval(
            f"SELECT product_id FROM products ORDER BY -product_id"
        )
        location_ids = await self.pool.fetch(
            f"SELECT location_id FROM locations"
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
                except asyncpg.exceptions.UniqueViolationError:
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        product_id = await self.pool.fetchval(
            f"SELECT product_id FROM products ORDER BY -product_id"
        )
        location_ids = await self.pool.fetch(
            f"SELECT location_id FROM locations"
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
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1
        return product_id

    async def add_product_size(self, size_product_id, size_name, prices):
        """Добавляем размер товара товар"""
        sql = """
                INSERT INTO product_sizes (size_product_id, size_name, price_1, price_2, price_3, price_4, price_5, 
                price_6) 
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
            except asyncpg.exceptions.UniqueViolationError:
                count += 1
        size_id = await self.pool.fetchval(
            f"SELECT size_id FROM product_sizes ORDER BY -size_id"
        )
        location_ids = await self.pool.fetch(
            f"SELECT location_id FROM locations"
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
                except asyncpg.exceptions.UniqueViolationError:
                    count_cat += 1

    async def get_product_info(self, product_id):
        """Получаем информацию о товаре"""
        return await self.pool.fetchrow(
            f"SELECT * FROM products WHERE product_id = {product_id}"
        )

    async def get_product_sizes(self, product_id):
        """Получаем размеры товара"""
        return await self.pool.fetch(
            f"SELECT * FROM product_sizes WHERE size_product_id = {product_id}"
        )

    async def get_category_for_admin_true(self):
        """Выбираем все категории, доступные для проажи"""
        return await self.pool.fetch(
            f"""SELECT category_id, category_name FROM categories WHERE is_category_available=true 
ORDER BY category_id"""
        )

    async def get_category_for_admin_false(self):
        """Выбираем все категории, снятые с проажи"""
        return await self.pool.fetch(
            f"""SELECT category_id, category_name FROM categories WHERE is_category_available=false ORDER BY category_id"""
        )

    async def get_category_for_admin(self):
        """Выбираем все категории, в которых есть снятые с продажи товары"""
        return await self.pool.fetch(
            f"""SELECT DISTINCT category_id, category_name 
FROM categories
JOIN products ON product_category_id=category_id
WHERE is_product_available = false ORDER BY category_id"""
        )

    async def get_category_for_remove_item_from_stock(self):
        """Выбираем все категории, в которых есть товары в продаже"""
        return await self.pool.fetch(
            f"""SELECT DISTINCT  category_id, category_name 
    FROM  products
    JOIN categories ON product_category_id=category_id
    WHERE is_product_available = true ORDER BY category_id"""
        )

    async def get_products_for_remove_from_stock(self, category_id):
        """Выбираем товары из категории чтобы свять с продажи"""
        return await self.pool.fetch(
            f"""SELECT product_id, product_name FROM products
WHERE product_category_id = {category_id} AND is_product_available = true ORDER BY product_id"""
        )

    async def get_products_for_return_to_stock(self, category_id):
        """Выбираем товары из категории"""
        return await self.pool.fetch(
            f"""SELECT product_id, product_name FROM products
    WHERE product_category_id = {category_id} AND is_product_available = false ORDER BY product_id"""
        )

    async def change_seller_admin_location(self, seller_admin_id, metro_id, location_id):
        """Меняем привязку к локации у продавца админа"""
        await self.pool.execute(
            f"""UPDATE admin_sellers SET admin_seller_metro_id={metro_id}, admin_seller_location_id={location_id}
WHERE admin_seller_id={seller_admin_id}"""
        )

    async def change_seller_location(self, seller_id, metro_id, location_id):
        """Меняем привязку к локации у продавца"""
        await self.pool.execute(
            f"""UPDATE sellers SET seller_metro_id={metro_id}, seller_location_id={location_id}
    WHERE seller_id={seller_id}"""
        )

    async def change_courier_location(self, courier_id, metro_id, location_id):
        """Меняем привязку к локации у курьера"""
        await self.pool.execute(
            f"""UPDATE couriers SET courier_metro_id={metro_id}, courier_location_id={location_id}
    WHERE courier_id={courier_id}"""
        )

    async def get_seller_admin_name_id(self, seller_admin_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""SELECT admin_seller_name, admin_seller_telegram_id FROM admin_sellers
WHERE admin_seller_id={seller_admin_id}"""
        )

    async def get_seller_name_id(self, seller_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""SELECT seller_name, seller_telegram_id FROM sellers
    WHERE seller_id={seller_id}"""
        )

    async def get_courier_name_id(self, courier_id):
        """Получаем имя и tg_id"""
        return await self.pool.fetchrow(
            f"""SELECT courier_name, courier_telegram_id FROM couriers
    WHERE courier_id={courier_id}"""
        )

    async def edit_metro_name(self, metro_id, metro_name):
        """Меняем название станции метро"""
        await self.pool.execute(
            f"""UPDATE metro SET metro_name='{metro_name}' WHERE metro_id={metro_id}"""
        )

    async def get_categories_with_products(self):
        """Все категории, в которых есть товары"""
        return await self.pool.fetch(
            f"""SELECT category_id, category_name 
FROM categories
JOIN products ON product_category_id=category_id ORDER BY product_category_id"""
        )

    async def product_has_size(self, product_id):
        """Проверяем есть ли у товара размеры"""
        return await self.pool.fetchval(
            f"SELECT EXISTS(SELECT size_product_id FROM product_sizes WHERE size_product_id={product_id})"
        )

    async def edit_product_name(self, product_id, product_name):
        """Обновляем название товара"""
        await self.pool.execute(
            f"""UPDATE products SET product_name='{product_name}' WHERE product_id={product_id}"""
        )

    async def edit_product_description(self, product_id, product_description):
        """Обновляем описание товара"""
        await self.pool.execute(
            f"""UPDATE products SET product_description='{product_description}' WHERE product_id={product_id}"""
        )

    async def edit_product_photo(self, product_id, product_photo_id):
        """Обновляем фотографию товара"""
        await self.pool.execute(
            f"""UPDATE products SET product_photo_id='{product_photo_id}' WHERE product_id={product_id}"""
        )

    async def edit_product_prices(self, product_id, prices):
        """Обновляем цены товара"""
        await self.pool.execute(
            f"""UPDATE products SET price_1={prices['price1']}, price_2={prices['price2']}, price_3={prices['price3']},
price_4={prices['price4']}, price_5={prices['price5']}, price_6={prices['price6']}
WHERE product_id={product_id}"""
        )

    async def item_is_available(self, product_id):
        """Проверяем в продаже товар или нет"""
        return await self.pool.fetchval(
            f"""SELECT is_product_available FROM products WHERE product_id={product_id}"""
        )

    async def remove_size_by_id(self, size_id):
        """Удаляем размер"""
        await self.pool.execute(
            f"""DELETE FROM product_sizes WHERE size_id = {size_id}"""
        )

    async def get_size_info_by_id(self, size_id):
        """Получаем инфу о размере"""
        return await self.pool.fetchrow(
            f"""SELECT * FROM product_sizes WHERE size_id = {size_id}"""
        )

    async def edit_size_name(self, size_id, size_name):
        """Меняем название размера"""
        await self.pool.execute(
            f"""UPDATE product_sizes SET size_name='{size_name}' WHERE size_id={size_id}"""
        )

    async def edit_size_prices(self, size_id, prices):
        """Меняем цены размера"""
        await self.pool.execute(
            f"""UPDATE product_sizes SET price_1={prices['price1']}, price_2={prices['price2']}, 
price_3={prices['price3']}, price_4={prices['price4']}, price_5={prices['price5']}, price_6={prices['price6']}
WHERE size_id={size_id}"""
        )

    async def get_location_by_seller_admin_id(self, seller_admin_id):
        """Получаем id локации по id seller-admina"""
        return await self.pool.fetchrow(
            f"""SELECT admin_seller_location_id, admin_seller_metro_id FROM admin_sellers WHERE admin_seller_telegram_id = {seller_admin_id}"""
        )

    async def get_location_for_seller_admin(self, seller_admin_id):
        """Получаем id локации по id seller-admina"""
        return await self.pool.fetchval(
            f"""SELECT admin_seller_location_id FROM admin_sellers WHERE admin_seller_telegram_id = {seller_admin_id}"""
        )

    async def get_seller_location(self, seller_id):
        """Получаем id локации продацва"""
        return await self.pool.fetchval(
            f"""SELECT seller_location_id FROM sellers WHERE seller_id = {seller_id}"""
        )

    async def get_courier_location(self, courier_id):
        """Получаем id локации курьера"""
        return await self.pool.fetchval(
            f"""SELECT courier_location_id FROM couriers WHERE courier_id = {courier_id}"""
        )

    async def get_sellers_list_by_location(self, location_id):
        """Получаем список продавцов в локации"""
        return await self.pool.fetch(
            f"""SELECT seller_id, seller_name, seller_telegram_id FROM sellers WHERE seller_location_id={location_id}"""
        )

    async def get_courier_list_by_location(self, location_id):
        """Получаем список курьеров в локации"""
        return await self.pool.fetch(
            f"""SELECT courier_id, courier_name, courier_telegram_id FROM couriers WHERE courier_location_id={location_id}"""
        )

    async def get_categories_in_stock_by_location(self, location_id, status):
        """Получаем категорию, доступную для пользователя"""
        return await self.pool.fetch(
            f"""SELECT category_id, category_name 
FROM locations_categories
JOIN categories  ON lc_category_id=category_id
WHERE  lc_location_id = {location_id}
AND is_category_in_location_available = {status}
ORDER BY category_id;"""
        )

    async def get_category_for_stock_item_in_location(self, location_id, status):
        """Достаем категории с товарами"""
        return await self.pool.fetch(
            f"""SELECT DISTINCT category_id, category_name 
FROM categories
JOIN products ON product_category_id=category_id
JOIN locations_products ON lp_product_id = product_id
WHERE is_product_in_location_available = {status} 
AND lp_location_id = {location_id}
ORDER BY category_id;"""
        )

    async def get_products_for_stock_in_location(self, location_id, category_id, status):
        """Получаем товары из категории"""
        return await self.pool.fetch(
            f"""SELECT product_id, product_name 
FROM categories
JOIN products ON product_category_id=category_id
JOIN locations_products ON lp_product_id = product_id
WHERE is_product_in_location_available = {status} 
AND lp_location_id = {location_id}
AND category_id = {category_id}
ORDER BY product_category_id;"""
        )

    async def get_orders_for_user(self, user_id):
        """Получаем активные ордеры"""
        return await self.pool.fetch(
            f"""SELECT order_id, deliver_to, delivery_method, order_info, order_price, order_status
FROM orders WHERE order_user_telegram_id={user_id}
AND order_status = 'Ожидание подтверждения продавца'
OR order_status='Подтвержден, готовится' 
OR order_status='Заказ готов'
ORDER BY order_id"""
        )

    async def im_at_work_seller(self, user_id, status):
        """Устанавливаем статус продавца"""
        await self.pool.execute(
            f"""UPDATE sellers SET seller_status={status} WHERE seller_telegram_id = {user_id}"""
        )

    async def im_at_work_courier(self, user_id, status):
        """Устанавливаем статус продавца"""
        await self.pool.execute(
            f"""UPDATE couriers SET courier_status={status} WHERE courier_telegram_id = {user_id}"""
        )

    async def set_about(self, about):
        """Добавляем/изменяем инфу о компании"""
        await self.pool.execute(
            f"""DELETE FROM about"""
        )
        sql = "INSERT INTO about (info) VALUES ($1)"
        await self.pool.execute(sql, about)

    async def get_about(self):
        """Получаем инфу о компании"""
        return await self.pool.fetchval(
            f"""SELECT info FROM about"""
        )

    async def get_objects(self):
        """Получаем список с названиями точек доставки"""
        return await self.pool.fetch(
            f"""SELECT local_object_name from local_objects"""
        )

    async def get_users_id(self):
        """Получаем список пользователей"""
        return await self.pool.fetch(
            f"""SELECT user_telegram_id FROM users"""
        )

    async def is_banned(self, user_id):
        """Проверяем забанен ли"""
        return await self.pool.fetchval(
            f"""SELECT is_banned FROM users WHERE user_telegram_id={user_id}"""
        )

    async def get_reason_for_ban(self, user_id):
        """Проверяем забанен ли"""
        return await self.pool.fetchval(
            f"""SELECT reason_for_ban FROM users WHERE user_telegram_id={user_id}"""
        )

    async def ban_user(self, user_id, reason):
        """Блокируем пользователя"""
        await self.pool.execute(
            f"""UPDATE users SET is_banned=true, reason_for_ban='{reason}'
                WHERE user_telegram_id={user_id}"""
        )

    async def unban_user(self, user_id):
        """Разблокируем пользователя"""
        await self.pool.execute(
            f"""UPDATE users SET is_banned=false
                WHERE user_telegram_id={user_id}"""
        )
