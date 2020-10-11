from loader import db

h_format = {
    'bold': True,
    'border': 2,
    'align': 'center',
    'valign': 'vcenter',
    'text_wrap': True
}
b_format = {
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'text_wrap': True
}


async def get_indicators(workbook, indicators, bonus_indicators):
    """Собираем таблицу Статистика по заказам"""
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)
    worksheet = workbook.add_worksheet('Показатели за период')

    worksheet.set_column(0, 0, 1)

    worksheet.write('B4', 'Показатели за период', head_format)
    worksheet.set_column(1, 1, 40)
    worksheet.write('C4', 'Кол-во', head_format)
    worksheet.set_column(2, 2, 20)
    worksheet.write('D4', 'На сумму (руб)', head_format)
    worksheet.set_column(3, 3, 20)
    worksheet.write('B5', 'Всего заказов', body_format)
    worksheet.write('B6', 'в т.ч. Выполнено', body_format)
    worksheet.write('B7', 'в т.ч. Отменен покупателем', body_format)
    worksheet.write('B8', 'в т.ч. Отменен продавцом', body_format)
    worksheet.write('B9', 'в т.ч. Отменен курьером', body_format)

    if indicators:
        worksheet.write('C5', f'{indicators["all_orders"]}', body_format)
        worksheet.write('C6', f'{indicators["completed"]}', body_format)
        worksheet.write('C7', f'{indicators["canceled_by_client"]}', body_format)
        worksheet.write('C8', f'{indicators["canceled_by_seller"]}', body_format)
        worksheet.write('C9', f'{indicators["canceled_by_courier"]}', body_format)


        worksheet.write('D5', f'{indicators["all_orders_price"]}', body_format)
        worksheet.write('D6', f'{indicators["completed_price"]}', body_format)
        worksheet.write('D7', f'{indicators["canceled_by_client_price"]}', body_format)
        worksheet.write('D8', f'{indicators["canceled_by_seller_price"]}', body_format)
        worksheet.write('D9', f'{indicators["canceled_by_courier_price"]}', body_format)

    worksheet.write('F4', 'Показатели за период (бонусные заказы)', head_format)
    worksheet.set_column(5, 5, 40)
    worksheet.write('G4', 'Кол-во', head_format)
    worksheet.set_column(6, 6, 20)
    worksheet.write('F5', 'Всего заказов', body_format)
    worksheet.write('F6', 'в т.ч. Выполнено', body_format)
    worksheet.write('F7', 'в т.ч. Отменен покупателем', body_format)
    worksheet.write('F8', 'в т.ч. Отменен продавцом', body_format)

    if bonus_indicators:
        worksheet.write('G5', f'{bonus_indicators["all_orders"]}', body_format)
        worksheet.write('G6', f'{bonus_indicators["completed"]}', body_format)
        worksheet.write('G7', f'{bonus_indicators["canceled_by_client"]}', body_format)
        worksheet.write('G8', f'{bonus_indicators["canceled_by_seller"]}', body_format)


async def get_order_statistics(workbook, orders, start_period, end_period):
    """Собираем таблицу Статистика по заказам"""
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet = workbook.add_worksheet('Статистика заказов')

    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Локация\nдоставки', head_format)
    worksheet.set_column(4, 4, 30)
    worksheet.merge_range('F2:F3', 'ID\nпродавца', head_format)
    worksheet.merge_range('G2:G3', 'ID\nкурьера', head_format)
    worksheet.merge_range('H2:H3', 'ID\nклиента', head_format)
    worksheet.merge_range('I2:I3', 'Дата\nзаказа', head_format)
    worksheet.merge_range('J2:J3', 'Время\nзаказа', head_format)
    worksheet.merge_range('K2:K3', 'Доставить\nчерез\n(мин)', head_format)
    worksheet.merge_range('L2:L3', 'Время\nпринятия\nзаказа', head_format)
    worksheet.merge_range('M2:M3', 'Время\nдоставки\nзаказа', head_format)
    worksheet.merge_range('N2:N3', 'Время\nотмены\nзаказа', head_format)
    worksheet.merge_range('O2:O3', '№\nзаказа', head_format)
    worksheet.set_column(5, 13, 10)
    worksheet.set_column(14, 14, 8)
    worksheet.merge_range('P2:P3', 'Заказанные позиции', head_format)
    worksheet.set_column(15, 15, 30)
    worksheet.merge_range('Q2:Q3', 'Кол-во', head_format)
    worksheet.merge_range('R2:R3', 'Цена\nза ед.\n(руб)', head_format)
    worksheet.merge_range('S2:S3', 'Сумма\nзаказа\n(руб)', head_format)
    worksheet.set_column(16, 17, 10)
    worksheet.merge_range('T2:T3', 'Метод\nдоставки', head_format)
    worksheet.set_column(19, 19, 13)
    worksheet.merge_range('U2:U3', 'Статус\nзаказа', head_format)
    worksheet.set_column(20, 20, 20)
    worksheet.merge_range('V2:V3', 'Отзыв\nклиента', head_format)
    worksheet.merge_range('W2:W3', 'Причина\nотмены', head_format)
    worksheet.set_column(21, 22, 30)

    first_string = 4
    num = 1
    if orders:
        for order in orders:
            products = await db.get_order_products(order['order_id'])
            local_object_name = await db.get_local_object_name_by_id(order['order_local_object_id'])

            if len(products) > 1:
                last_string = len(products) + first_string - 1
                worksheet.merge_range(f'B{first_string}:B{last_string}', f'{num}', body_format)
                worksheet.merge_range(f'C{first_string}:C{last_string}', f'{start_period}', body_format)
                worksheet.merge_range(f'D{first_string}:D{last_string}', f'{end_period}', body_format)
                worksheet.merge_range(f'E{first_string}:E{last_string}', f'{local_object_name}', body_format)
                if order["order_seller_id"]:
                    worksheet.merge_range(f'F{first_string}:F{last_string}', f'{order["order_seller_id"]}', body_format)
                else:
                    worksheet.merge_range(f'F{first_string}:F{last_string}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.merge_range(f'G{first_string}:G{last_string}', f'{order["order_courier_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'G{first_string}:G{last_string}', f'', body_format)
                worksheet.merge_range(f'H{first_string}:H{last_string}', f'{order["order_user_id"]}', body_format)
                worksheet.merge_range(f'I{first_string}:I{last_string}', f'{order["order_date"].strftime("%d.%m.%Y")}',
                                      body_format)
                worksheet.merge_range(f'J{first_string}:J{last_string}',
                                      f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                      body_format)
                worksheet.merge_range(f'K{first_string}:K{last_string}', f'{order["order_deliver_through"]}',
                                      body_format)
                if order["order_accepted_at"]:
                    worksheet.merge_range(f'L{first_string}:L{last_string}',
                                          f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'L{first_string}:L{last_string}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.merge_range(f'M{first_string}:M{last_string}',
                                          f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'M{first_string}:M{last_string}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.merge_range(f'N{first_string}:N{last_string}',
                                          f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'N{first_string}:N{last_string}', f'', body_format)
                worksheet.merge_range(f'O{first_string}:O{last_string}', f'{order["order_id"]}', body_format)
                worksheet.merge_range(f'S{first_string}:S{last_string}', f'{order["order_final_price"]}', body_format)
                worksheet.merge_range(f'T{first_string}:T{last_string}', f'{order["order_delivery_method"]}',
                                      body_format)
                worksheet.merge_range(f'U{first_string}:U{last_string}', f'{order["order_status"]}', body_format)
                if order["order_review"]:
                    worksheet.merge_range(f'V{first_string}:V{last_string}', f'{order["order_review"]}', body_format)
                else:
                    worksheet.merge_range(f'V{first_string}:V{last_string}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.merge_range(f'W{first_string}:W{last_string}', f'{order["order_reason_for_rejection"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'W{first_string}:W{last_string}', f'', body_format)
                first_prod_line = first_string
                for prod in products:
                    worksheet.write(f'P{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1
                first_string = last_string + 1
            else:
                worksheet.write(f'B{first_string}', f'{num}', body_format)
                worksheet.write(f'C{first_string}', f'{start_period}', body_format)
                worksheet.write(f'D{first_string}', f'{end_period}', body_format)
                worksheet.write(f'E{first_string}', f'{local_object_name}', body_format)
                if order["order_seller_id"]:
                    worksheet.write(f'F{first_string}', f'{order["order_seller_id"]}', body_format)
                else:
                    worksheet.write(f'F{first_string}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.write(f'G{first_string}', f'{order["order_courier_id"]}', body_format)
                else:
                    worksheet.write(f'G{first_string}', f'', body_format)
                worksheet.write(f'H{first_string}', f'{order["order_user_id"]}', body_format)
                worksheet.write(f'I{first_string}', f'{order["order_date"].strftime("%d.%m.%Y")}',
                                body_format)
                worksheet.write(f'J{first_string}', f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                body_format)
                worksheet.write(f'K{first_string}', f'{order["order_deliver_through"]}', body_format)
                if order["order_accepted_at"]:
                    worksheet.write(f'L{first_string}', f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'L{first_string}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.write(f'M{first_string}', f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'M{first_string}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.write(f'N{first_string}', f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'N{first_string}', f'', body_format)
                worksheet.write(f'O{first_string}', f'{order["order_id"]}', body_format)
                worksheet.write(f'S{first_string}', f'{order["order_final_price"]}', body_format)
                worksheet.write(f'T{first_string}', f'{order["order_delivery_method"]}', body_format)
                worksheet.write(f'U{first_string}', f'{order["order_status"]}', body_format)
                if order["order_review"]:
                    worksheet.write(f'V{first_string}', f'{order["order_review"]}', body_format)
                else:
                    worksheet.write(f'V{first_string}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.write(f'W{first_string}', f'{order["order_reason_for_rejection"]}',
                                    body_format)
                else:
                    worksheet.write(f'W{first_string}', f'', body_format)
                first_prod_line = first_string
                for prod in products:
                    worksheet.write(f'P{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1
                first_string += 1
            num += 1


async def get_bonus_order_statistics(workbook, orders, start_period, end_period):
    """Собираем таблицу Статистика по заказам"""
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet = workbook.add_worksheet('Статистика бонусных заказов')

    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)  # 4
    worksheet.merge_range('E2:E3', 'ID\nпродавца', head_format)
    worksheet.set_column(4, 12, 10)
    worksheet.merge_range('F2:F3', 'ID\nклиента', head_format)
    worksheet.merge_range('G2:G3', 'Дата\nзаказа', head_format)
    worksheet.merge_range('H2:H3', 'Время\nзаказа', head_format)
    worksheet.merge_range('I2:I3', 'Время\nпринятия\nзаказа', head_format)
    worksheet.merge_range('J2:J3', 'Время\nвыдачи\nзаказа', head_format)
    worksheet.merge_range('K2:K3', 'Время\nотмены\nзаказа', head_format)
    worksheet.merge_range('L2:L3', '№\nзаказа', head_format)
    worksheet.merge_range('M2:M3', 'Кол-во', head_format)
    worksheet.merge_range('N2:N3', 'Статус\nзаказа', head_format)
    worksheet.set_column(13, 13, 20)
    worksheet.merge_range('O2:O3', 'Отзыв\nклиента', head_format)
    worksheet.merge_range('P2:P3', 'Причина\nотмены', head_format)
    worksheet.set_column(14, 15, 30)

    first_string = 4
    num = 1
    if orders:
        for order in orders:
            worksheet.write(f'B{first_string}', f'{num}', body_format)
            worksheet.write(f'C{first_string}', f'{start_period}', body_format)
            worksheet.write(f'D{first_string}', f'{end_period}', body_format)
            if order["bonus_order_seller_id"]:
                worksheet.write(f'E{first_string}', f'{order["bonus_order_seller_id"]}', body_format)
            else:
                worksheet.write(f'E{first_string}', f'', body_format)
            worksheet.write(f'F{first_string}', f'{order["bonus_order_user_id"]}', body_format)
            worksheet.write(f'G{first_string}', f'{order["bonus_order_date"].strftime("%d.%m.%Y")}',
                            body_format)
            worksheet.write(f'H{first_string}', f'{order["bonus_order_created_at"].strftime("%H:%M:%S")}',
                            body_format)
            if order["bonus_order_accepted_at"]:
                worksheet.write(f'I{first_string}', f'{order["bonus_order_accepted_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'I{first_string}', f'', body_format)
            if order["bonus_order_delivered_at"]:
                worksheet.write(f'J{first_string}', f'{order["bonus_order_delivered_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'J{first_string}', f'', body_format)
            if order["bonus_order_canceled_at"]:
                worksheet.write(f'K{first_string}', f'{order["bonus_order_canceled_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'K{first_string}', f'', body_format)
            worksheet.write(f'L{first_string}', f'{order["bonus_order_id"]}', body_format)
            worksheet.write(f'M{first_string}', f'{order["bonus_order_quantity"]}', body_format)
            worksheet.write(f'N{first_string}', f'{order["bonus_order_status"]}', body_format)
            if order["bonus_order_review"]:
                worksheet.write(f'O{first_string}', f'{order["bonus_order_review"]}', body_format)
            else:
                worksheet.write(f'O{first_string}', f'', body_format)
            if order["bonus_order_reason_for_rejection"]:
                worksheet.write(f'P{first_string}', f'{order["bonus_order_reason_for_rejection"]}',
                                body_format)
            else:
                worksheet.write(f'P{first_string}', f'', body_format)
            first_string += 1
            num += 1


async def get_seller_statistics(workbook, sellers, start_period, end_period, by_date=None, first_date=None,
                                last_date=None):
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet = workbook.add_worksheet('Продавцы')

    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 5, 15)
    worksheet.set_column(6, 6, 25)
    worksheet.set_column(7, 7, 15)
    worksheet.set_column(8, 8, 10)
    worksheet.set_column(9, 9, 15)
    worksheet.set_column(10, 10, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'ID\nпродавца', head_format)
    worksheet.merge_range('F2:F3', 'telegramID\nпродавца', head_format)
    worksheet.merge_range('G2:G3', 'Имя продавца', head_format)
    worksheet.merge_range('H2:I2', 'Заказы', head_format)
    worksheet.write('H3', 'наименование', head_format)
    worksheet.write('I3', 'кол-во', head_format)
    worksheet.merge_range('J2:K2', 'Бонусные аказы', head_format)
    worksheet.write('J3', 'наименование', head_format)
    worksheet.write('K3', 'кол-во', head_format)

    first_string = 4
    num = 1

    if sellers:
        for seller in sellers:
            if by_date:
                data = await db.get_seller_info_by_date(seller["order_seller_id"], by_date)
            elif first_date:
                data = await db.get_seller_info_by_date_period(seller["order_seller_id"], first_date, last_date)
            else:
                data = await db.get_seller_info(seller["order_seller_id"])

            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{seller["order_seller_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{data["seller_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{data["seller_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{data["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{data["completed_orders"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'I{first_string + 2}', f'{data["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'I{first_string + 3}', f'{data["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'I{first_string + 4}', f'{data["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'{data["all_bonus_orders"]}', body_format)
            worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'Выполнено', body_format)
            worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'{data["completed_bonus_orders"]}',
                                  body_format)
            worksheet.write(f'J{first_string + 4}', f'Отменено', body_format)
            worksheet.write(f'K{first_string + 4}', f'{data["canceled_bonus_orders"]}', body_format)
            first_string += 5
            num += 1


async def get_courier_statistics(workbook, couriers, start_period, end_period, by_date=None, first_date=None,
                                last_date=None):
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet = workbook.add_worksheet('Курьеры')

    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 5, 15)
    worksheet.set_column(6, 6, 25)
    worksheet.set_column(7, 7, 15)
    worksheet.set_column(8, 8, 10)
    worksheet.set_column(9, 9, 15)
    worksheet.set_column(10, 10, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'ID\nкурьера', head_format)
    worksheet.merge_range('F2:F3', 'telegramID\nкурьера', head_format)
    worksheet.merge_range('G2:G3', 'Имя курьера', head_format)
    worksheet.merge_range('H2:I2', 'Заказы', head_format)
    worksheet.write('H3', 'наименование', head_format)
    worksheet.write('I3', 'кол-во', head_format)

    first_string = 4
    num = 1

    if couriers:
        for courier in couriers:
            if by_date:
                data = await db.get_courier_info_by_date(courier["order_courier_id"], by_date)
            elif first_date:
                data = await db.get_courier_info_by_date_period(courier["order_courier_id"], first_date, last_date)
            else:
                data = await db.get_courier_info(courier["order_courier_id"])

            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{courier["order_courier_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{data["courier_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{data["courier_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{data["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{data["completed_orders"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'I{first_string + 2}', f'{data["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'I{first_string + 3}', f'{data["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'I{first_string + 4}', f'{data["canceled_by_client_orders"]}', body_format)
            first_string += 5
            num += 1


async def get_client_statistics(workbook, clients, location, start_period, end_period, by_date=None, first_date=None,
                                last_date=None):
    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet = workbook.add_worksheet('Клиенты')

    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 5, 15)
    worksheet.set_column(6, 6, 15)
    worksheet.set_column(7, 7, 10)
    worksheet.set_column(8, 8, 15)
    worksheet.set_column(9, 9, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'ID\nклиента', head_format)
    worksheet.merge_range('F2:F3', 'telegramID\nклиента', head_format)
    worksheet.merge_range('G2:H2', 'Заказы', head_format)
    worksheet.write('G3', 'наименование', head_format)
    worksheet.write('H3', 'кол-во', head_format)
    worksheet.merge_range('I2:J2', 'Бонусные аказы', head_format)
    worksheet.write('I3', 'наименование', head_format)
    worksheet.write('J3', 'кол-во', head_format)

    first_string = 4
    num = 1

    if clients:
        for client in clients:
            if by_date:
                data = await db.get_client_info_by_date(client["order_user_id"], location, by_date)
            elif first_date:
                data = await db.get_client_info_by_date_period(client["order_user_id"], location, first_date, last_date)
            else:
                data = await db.get_client_info(client["order_user_id"], location)

            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{client["order_user_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{data["user_telegram_id"]}', body_format)
            worksheet.write(f'G{first_string}', f'Всего', body_format)
            worksheet.write(f'H{first_string}', f'{data["all_orders"]}', body_format)
            worksheet.write(f'G{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'H{first_string + 1}', f'{data["completed_orders"]}', body_format)
            worksheet.write(f'G{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'H{first_string + 2}', f'{data["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'G{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'H{first_string + 3}', f'{data["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'G{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'H{first_string + 4}', f'{data["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'I{first_string}:I{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'{data["all_bonus_orders"]}', body_format)
            worksheet.merge_range(f'I{first_string + 2}:I{first_string + 3}', f'Выполнено', body_format)
            worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'{data["completed_bonus_orders"]}',
                                  body_format)
            worksheet.write(f'I{first_string + 4}', f'Отменено', body_format)
            worksheet.write(f'J{first_string + 4}', f'{data["canceled_bonus_orders"]}', body_format)
            first_string += 5
            num += 1
