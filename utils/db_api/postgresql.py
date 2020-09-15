import asyncio
import asyncpg
from datetime import datetime

from data import config

now = datetime.now()


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool: asyncio.pool.Pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=config.PGUSER,
                database=config.PGDATABASE,
                password=config.PGPASSWORD,
                host=config.ip,
                port=config.PORT,
                statement_cache_size=0
            )
        )

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
        product_category_id INT NOT NULL,
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
        FOREIGN KEY (product_category_id) REFERENCES categories (category_id) ON UPDATE CASCADE);
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
                lc_category_id INT REFERENCES categories (category_id) ON UPDATE CASCADE,
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
                admin_telegram_id INT NOT NULL UNIQUE
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
           FOREIGN KEY (user_metro_id) REFERENCES metro (metro_id) ON DELETE SET NULL,
           FOREIGN KEY (user_location_id) REFERENCES locations (location_id) ON DELETE SET NULL
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

    async def get_available_metro(self):
        """Получаем список доступных станций метро"""
        return await self.pool.fetch(
            "SELECT metro_id, metro_name  FROM metro where is_metro_available = TRUE")

    async def get_metro_name_by_metro_id(self, metro_id):
        """Получаем название станции метро по его id"""
        return await self.pool.fetchval(f"SELECT metro_name FROM metro WHERE metro_id = {metro_id}")

    async def get_available_locations(self, metro_id):
        """Получаем список доступных локаций около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT location_id, location_name  FROM locations where location_metro_id = {metro_id} AND is_location_available = TRUE")

    async def get_available_local_objects(self, metro_id):
        """Получаем список доступных объектов доставки около заданной станции метро"""
        return await self.pool.fetch(
            f"SELECT local_object_id, local_object_name  FROM local_objects where local_object_metro_id = {metro_id} AND is_local_object_available = TRUE")

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
            while not done:
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError:
                    pass

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
            while not done:
                try:
                    await self.pool.execute(sql, user_telegram_id, user_metro_id, user_location_id,
                                            user_local_object_id, inviter_id)
                    done = True
                except asyncpg.exceptions.UniqueViolationError:
                    pass

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

    async def get_categories_for_user_location_id(self, user_id, ):
        """Получаем список доступных категорий в локации пользователя"""
        sql = f"""
        SELECT categories.category_name, categories.category_id
        FROM locations_categories JOIN categories ON locations_categories.lc_category_id=categories.category_id
        WHERE locations_categories.lc_location_id=
        (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
        AND locations_categories.is_category_in_location_available = true AND categories.is_category_available = true
        ORDER BY category_id;
        """
        return await self.pool.fetch(sql)

    async def get_product_for_user_location_id(self, user_id, category_id):
        """Получаем список доступных товаров в локации пользователя"""
        sql = f"""
        SELECT products.product_name, products.product_id
        FROM locations_products JOIN products ON locations_products.lp_product_id=products.product_id
        WHERE products.product_category_id = {category_id}
		AND locations_products.lp_location_id=
        (SELECT user_location_id FROM users WHERE user_telegram_id = {user_id})
        AND locations_products.is_product_in_location_available = true AND products.is_product_available = true
		ORDER BY product_id;
        """
        return await self.pool.fetch(sql)

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
        while not done:
            try:
                await self.pool.execute(sql, user_id, order_detail['product_id'], order_detail['size_id'],
                                        order_detail['product_name'], order_detail['product_price'],
                                        order_detail['quantity'], order_detail['order_price'])
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                pass

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
        while not done:
            try:
                await self.pool.execute(sql, order_user_telegram_id, order_metro_id, order_location_id,
                                        order_local_object_id,
                                        order_local_object_name, delivery_method, order_info, order_price, order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                pass

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
        while not done:
            try:
                await self.pool.execute(sql, order_user_telegram_id, order_metro_id, order_location_id,
                                        order_local_object_id, order_local_object_name, delivery_method,
                                        delivery_address, order_info, order_price, order_status)
                done = True
            except asyncpg.exceptions.UniqueViolationError:
                pass

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

    async def get_size_info(self, size_id):
        """Получаем информацию о размере"""
        return await self.pool.fetchrow(
            f'SELECT size_name, size_product_id, price_1, price_2, price_3, price_4, price_5, price_6 from product_sizes where size_id = {size_id}'
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
            WHERE order_location_id = {location_id} AND order_status = 'Заказ готов'
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
            inviter_id = int(num_user_and_inviter_id['inviter_id'])
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
