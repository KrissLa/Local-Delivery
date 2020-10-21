import asyncio
import logging
import os
import smtplib
import sys
import threading
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import xlsxwriter

from data.config import EMAIL_ADDRESS, EMAIL_PASSWORD
from loader import bot
from utils.emoji import success_em, error_em


async def send_admin_statistics(data):
    """Собираем и отправляем статистику админу"""

    loop = asyncio.get_running_loop()

    mail_was_send = await loop.run_in_executor(
        None, write_admin_statistics, data)
    if mail_was_send:
        await bot.send_message(data['user_id'], f"{success_em} Статистика отправлена Вам на почту {data['to_email']}.")
    else:
        await bot.send_message(data['user_id'],
                               f"{error_em} Не удалось отправить статистику по адресу {data['to_email']}."
                               f" Проверьте e-mail адрес и попробуйте еще раз.")


async def send_admin_delivery_statistics(data):
    """Собираем и отправляем статистику админу"""

    loop = asyncio.get_running_loop()

    mail_was_send = await loop.run_in_executor(
        None, write_admin_delivery_statistics, data)
    if mail_was_send:
        await bot.send_message(data['user_id'],
                               f"{success_em} Статистика по оптовым заказам отправлена Вам на почту {data['to_email']}.")
    else:
        await bot.send_message(data['user_id'],
                               f"{error_em} Не удалось отправить статистику по адресу {data['to_email']}."
                               f" Проверьте e-mail адрес и попробуйте еще раз.")


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


def send_confirm_mail(subject, body_text, to_email):
    """Отправка сообщения с уведомлением"""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEText(body_text)
    msg["From"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    server.quit()


def send_email(subject, body_text, to_email, file_to_attach=None, file_name=None):
    """
    Отправляем письмо со статистикой
    """
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    if body_text:
        msg.attach(MIMEText(body_text))

    attachment = MIMEBase('application', "octet-stream")

    try:
        with open(file_to_attach, "rb") as fh:
            data = fh.read()

        attachment.set_payload(data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=f"{file_name}.xlsx")
        msg.attach(attachment)
    except IOError:
        msg = f"Error opening attachment file {file_name}.xlsx"
        print(msg)
        sys.exit(1)

    server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    server.quit()

    # server.sendmail("arsavit@gmail.com", "arsavit@gmail.com", "go to bed!")


def get_orders(orders, products, numbers):
    """Формируем список"""
    num = 1
    first_line = 4
    for order in orders:
        order['order_products'] = []
        try:
            while products[0]['op_order_id'] == order['order_id']:
                order['order_products'].append(products[0])
                del products[0]
        except Exception as err:
            logging.error(err)
        try:
            while numbers[0]['order_id'] == order['order_id']:
                order['num'] = num
                order['first_line'] = first_line
                order['last_line'] = first_line + numbers[0]["count"] - 1
                first_line += numbers[0]["count"]
                num += 1
                del numbers[0]
        except Exception as err:
            logging.error(err)
    return orders


def get_delivery_orders(orders, products, numbers):
    """Формируем список"""
    num = 1
    first_line = 4
    for order in orders:
        order['order_products'] = []
        try:
            while products[0]['dop_order_id'] == order['delivery_order_id']:
                order['order_products'].append(products[0])
                del products[0]
        except Exception as err:
            logging.error(err)
        try:
            while numbers[0]['delivery_order_id'] == order['delivery_order_id']:
                order['num'] = num
                order['first_line'] = first_line
                order['last_line'] = first_line + numbers[0]["count"] - 1
                first_line += numbers[0]["count"]
                num += 1
                del numbers[0]
        except Exception as err:
            logging.error(err)
    return orders


def get_sellers_indicators(sellers, sellers_bonus):
    """Формируем список"""
    for sb in sellers_bonus:
        for seller in sellers:
            if sb['bonus_order_seller_id'] == seller['order_seller_id']:
                seller['all_bonus_orders'] = sb['all_bonus_orders']
                seller['completed_bonus_orders'] = sb['completed_bonus_orders']
                seller['canceled_bonus_orders'] = sb['canceled_bonus_orders']
                del sb
                break
    return sellers


def get_users_indicators(user_orders, user_bonus_orders):
    """Формируем список"""
    for ub in user_bonus_orders:
        for user in user_orders:
            if ub['bonus_order_user_id'] == user['order_user_id']:
                user['all_bonus_orders'] = ub['all_bonus_orders']
                user['completed_bonus_orders'] = ub['completed_bonus_orders']
                user['canceled_bonus_orders'] = ub['canceled_bonus_orders']
                del ub
                break
    return user_orders


def head_indicators(worksheet, head_format, body_format):
    """Шапка для первого листа"""
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

    worksheet.write('F4', 'Показатели за период (бонусные заказы)', head_format)
    worksheet.set_column(5, 5, 40)
    worksheet.write('G4', 'Кол-во', head_format)
    worksheet.set_column(6, 6, 20)
    worksheet.write('F5', 'Всего заказов', body_format)
    worksheet.write('F6', 'в т.ч. Выполнено', body_format)
    worksheet.write('F7', 'в т.ч. Отменен покупателем', body_format)
    worksheet.write('F8', 'в т.ч. Отменен продавцом', body_format)


def head_orders(worksheet, head_format):
    """Шапка второго листа"""
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


def head_bonus_orders(worksheet, head_format):
    """Шапка третьего листа"""
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


def head_sellers(worksheet, head_format):
    """Шапка четвертого листа"""
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


def head_couriers(worksheet, head_format):
    """Шапка пятого листа"""
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


def head_clients(worksheet, head_format):
    """Шапка шестого листа"""
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


def body_indicators(worksheet, body_format, indicators, bonus_indicators):
    """Записываем показатели"""
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

    if bonus_indicators:
        worksheet.write('G5', f'{bonus_indicators["all_orders"]}', body_format)
        worksheet.write('G6', f'{bonus_indicators["completed"]}', body_format)
        worksheet.write('G7', f'{bonus_indicators["canceled_by_client"]}', body_format)
        worksheet.write('G8', f'{bonus_indicators["canceled_by_seller"]}', body_format)


def body_orders(worksheet, body_format, orders, start_period, end_period):
    """Записываем заказы"""
    if orders:
        for order in orders:
            if len(order['order_products']) > 1:
                worksheet.merge_range(f'B{order["first_line"]}:B{order["last_line"]}', f'{order["num"]}', body_format)
                worksheet.merge_range(f'C{order["first_line"]}:C{order["last_line"]}', f'{start_period}', body_format)
                worksheet.merge_range(f'D{order["first_line"]}:D{order["last_line"]}', f'{end_period}', body_format)
                worksheet.merge_range(f'E{order["first_line"]}:E{order["last_line"]}', f'{order["local_object_name"]}',
                                      body_format)
                if order["order_seller_id"]:
                    worksheet.merge_range(f'F{order["first_line"]}:F{order["last_line"]}',
                                          f'{order["order_seller_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'F{order["first_line"]}:F{order["last_line"]}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.merge_range(f'G{order["first_line"]}:G{order["last_line"]}',
                                          f'{order["order_courier_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'G{order["first_line"]}:G{order["last_line"]}', f'', body_format)
                worksheet.merge_range(f'H{order["first_line"]}:H{order["last_line"]}', f'{order["order_user_id"]}',
                                      body_format)
                worksheet.merge_range(f'I{order["first_line"]}:I{order["last_line"]}',
                                      f'{order["order_date"].strftime("%d.%m.%Y")}',
                                      body_format)
                worksheet.merge_range(f'J{order["first_line"]}:J{order["last_line"]}',
                                      f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                      body_format)
                worksheet.merge_range(f'K{order["first_line"]}:K{order["last_line"]}',
                                      f'{order["order_deliver_through"]}',
                                      body_format)
                if order["order_accepted_at"]:
                    worksheet.merge_range(f'L{order["first_line"]}:L{order["last_line"]}',
                                          f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'L{order["first_line"]}:L{order["last_line"]}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.merge_range(f'M{order["first_line"]}:M{order["last_line"]}',
                                          f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'M{order["first_line"]}:M{order["last_line"]}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}',
                                          f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}', f'', body_format)
                worksheet.merge_range(f'O{order["first_line"]}:O{order["last_line"]}', f'{order["order_id"]}',
                                      body_format)
                worksheet.merge_range(f'S{order["first_line"]}:S{order["last_line"]}', f'{order["order_final_price"]}',
                                      body_format)
                worksheet.merge_range(f'T{order["first_line"]}:T{order["last_line"]}',
                                      f'{order["order_delivery_method"]}',
                                      body_format)
                worksheet.merge_range(f'U{order["first_line"]}:U{order["last_line"]}', f'{order["order_status"]}',
                                      body_format)
                if order["order_review"]:
                    worksheet.merge_range(f'V{order["first_line"]}:V{order["last_line"]}', f'{order["order_review"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'V{order["first_line"]}:V{order["last_line"]}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.merge_range(f'W{order["first_line"]}:W{order["last_line"]}',
                                          f'{order["order_reason_for_rejection"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'W{order["first_line"]}:W{order["last_line"]}', f'', body_format)
                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'P{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1
            else:
                worksheet.write(f'B{order["first_line"]}', f'{order["num"]}', body_format)
                worksheet.write(f'C{order["first_line"]}', f'{start_period}', body_format)
                worksheet.write(f'D{order["first_line"]}', f'{end_period}', body_format)
                worksheet.write(f'E{order["first_line"]}', f'{order["local_object_name"]}', body_format)
                if order["order_seller_id"]:
                    worksheet.write(f'F{order["first_line"]}', f'{order["order_seller_id"]}', body_format)
                else:
                    worksheet.write(f'F{order["first_line"]}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.write(f'G{order["first_line"]}', f'{order["order_courier_id"]}', body_format)
                else:
                    worksheet.write(f'G{order["first_line"]}', f'', body_format)
                worksheet.write(f'H{order["first_line"]}', f'{order["order_user_id"]}', body_format)
                worksheet.write(f'I{order["first_line"]}', f'{order["order_date"].strftime("%d.%m.%Y")}',
                                body_format)
                worksheet.write(f'J{order["first_line"]}', f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                body_format)
                worksheet.write(f'K{order["first_line"]}', f'{order["order_deliver_through"]}', body_format)
                if order["order_accepted_at"]:
                    worksheet.write(f'L{order["first_line"]}', f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'L{order["first_line"]}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.write(f'M{order["first_line"]}', f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'M{order["first_line"]}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.write(f'N{order["first_line"]}', f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'N{order["first_line"]}', f'', body_format)
                worksheet.write(f'O{order["first_line"]}', f'{order["order_id"]}', body_format)
                worksheet.write(f'S{order["first_line"]}', f'{order["order_final_price"]}', body_format)
                worksheet.write(f'T{order["first_line"]}', f'{order["order_delivery_method"]}', body_format)
                worksheet.write(f'U{order["first_line"]}', f'{order["order_status"]}', body_format)
                if order["order_review"]:
                    worksheet.write(f'V{order["first_line"]}', f'{order["order_review"]}', body_format)
                else:
                    worksheet.write(f'V{order["first_line"]}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.write(f'W{order["first_line"]}', f'{order["order_reason_for_rejection"]}',
                                    body_format)
                else:
                    worksheet.write(f'W{order["first_line"]}', f'', body_format)
                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'P{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1


def body_bonus_orders(worksheet, body_format, orders, start_period, end_period):
    """Записываем бонусные заказы"""
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


def body_sellers(worksheet, body_format, sellers, start_period, end_period):
    """Записываем продавцов"""
    if sellers:
        first_string = 4
        num = 1
        for seller in sellers:

            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{seller["order_seller_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{seller["seller_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{seller["seller_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{seller["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{seller["completed_orders"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'I{first_string + 2}', f'{seller["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'I{first_string + 3}', f'{seller["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'I{first_string + 4}', f'{seller["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'Выполнено', body_format)
            worksheet.write(f'J{first_string + 4}', f'Отменено', body_format)
            if 'all_bonus_orders' in seller:
                worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'{seller["all_bonus_orders"]}',
                                      body_format)
                worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'{seller["completed_bonus_orders"]}',
                                      body_format)
                worksheet.write(f'K{first_string + 4}', f'{seller["canceled_bonus_orders"]}', body_format)
            else:
                worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'', body_format)
                worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'', body_format)
                worksheet.write(f'K{first_string + 4}', f'', body_format)

            first_string += 5
            num += 1


def body_couriers(worksheet, body_format, couriers, start_period, end_period):
    """Записываем курьеров"""
    if couriers:
        first_string = 4
        num = 1
        for courier in couriers:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{courier["order_courier_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{courier["courier_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{courier["courier_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{courier["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{courier["completed_orders"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'I{first_string + 2}', f'{courier["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'I{first_string + 3}', f'{courier["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'I{first_string + 4}', f'{courier["canceled_by_client_orders"]}', body_format)
            first_string += 5
            num += 1


def body_clients(worksheet, body_format, clients, start_period, end_period):
    """Записываем клиентов"""
    if clients:
        first_string = 4
        num = 1
        for client in clients:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{client["order_user_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{client["user_telegram_id"]}', body_format)
            worksheet.write(f'G{first_string}', f'Всего', body_format)
            worksheet.write(f'H{first_string}', f'{client["all_orders"]}', body_format)
            worksheet.write(f'G{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'H{first_string + 1}', f'{client["completed_orders"]}', body_format)
            worksheet.write(f'G{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'H{first_string + 2}', f'{client["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'G{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'H{first_string + 3}', f'{client["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'G{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'H{first_string + 4}', f'{client["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'I{first_string}:I{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'I{first_string + 2}:I{first_string + 3}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 4}', f'Отменено', body_format)
            if "all_bonus_orders" in client:
                worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'{client["all_bonus_orders"]}',
                                      body_format)
                worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'{client["completed_bonus_orders"]}',
                                      body_format)
                worksheet.write(f'J{first_string + 4}', f'{client["canceled_bonus_orders"]}', body_format)
            else:
                worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'', body_format)
                worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'', body_format)
                worksheet.write(f'J{first_string + 4}', f'', body_format)

            first_string += 5
            num += 1


def write_statistics(data):
    """Записываем статистику"""
    orders = get_orders(data['orders'], data['products'], data['numbers'])

    users = get_users_indicators(data['user_orders'], data['user_bonus_orders'])

    sellers = get_sellers_indicators(data['sellers_orders'], data['sellers_bonus'])

    threads = []

    workbook = xlsxwriter.Workbook(data['path'])

    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet1 = workbook.add_worksheet('Показатели за период')
    worksheet2 = workbook.add_worksheet('Статистика заказов')
    worksheet3 = workbook.add_worksheet('Статистика бонусных заказов')
    worksheet4 = workbook.add_worksheet('Продавцы')
    worksheet5 = workbook.add_worksheet('Курьеры')
    worksheet6 = workbook.add_worksheet('Клиенты')

    x = threading.Thread(target=body_orders, args=(worksheet2, body_format, orders,
                                                   data['first_period'].strftime("%d.%m.%Y"),
                                                   data['end_period'].strftime("%d.%m.%Y")))
    x.start()
    threads.append(x)

    y = threading.Thread(target=body_bonus_orders,
                         args=(worksheet3, body_format, data['bonus_orders'], data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    y.start()
    threads.append(y)

    head_indicators(worksheet1, head_format, body_format)
    head_orders(worksheet2, head_format)
    head_bonus_orders(worksheet3, head_format)
    head_sellers(worksheet4, head_format)
    head_couriers(worksheet5, head_format)
    head_clients(worksheet6, head_format)

    body_indicators(worksheet1, body_format, data['indicators'], data['bonus_indicators'])

    body_sellers(worksheet4, body_format, sellers, data['first_period'].strftime("%d.%m.%Y"),
                 data['end_period'].strftime("%d.%m.%Y"))

    body_couriers(worksheet5, body_format, data['couriers_orders'], data['first_period'].strftime("%d.%m.%Y"),
                  data['end_period'].strftime("%d.%m.%Y"))

    body_clients(worksheet6, body_format, users, data['first_period'].strftime("%d.%m.%Y"),
                 data['end_period'].strftime("%d.%m.%Y"))

    for x in threads:
        x.join()

    workbook.close()
    try:
        send_email(data['file_name'], data['file_name'], data['to_email'], data['path'], data['file_name'])

        os.remove(data['path'])
        return True
    except Exception as err:
        logging.error(err)
        return False


def head_indicators_admin(worksheet, head_format, body_format):
    """Шапка для первого листа"""
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

    worksheet.write('B13', 'Показатели за период (бонусные заказы)', head_format)
    worksheet.write('C13', 'Кол-во', head_format)
    worksheet.write('B14', 'Всего заказов', body_format)
    worksheet.write('B15', 'в т.ч. Выполнено', body_format)
    worksheet.write('B16', 'в т.ч. Отменен покупателем', body_format)
    worksheet.write('B17', 'в т.ч. Отменен продавцом', body_format)

    worksheet.merge_range('F4:F5', 'Точка продаж', head_format)
    worksheet.set_column(5, 5, 40)
    worksheet.set_column(6, 15, 13)
    worksheet.merge_range('G4:H4', 'Всего', head_format)
    worksheet.merge_range('I4:J4', 'Выполнено', head_format)
    worksheet.merge_range('K4:L4', 'Отменено покупателем', head_format)
    worksheet.merge_range('M4:N4', 'Отменено продавцом', head_format)
    worksheet.merge_range('O4:P4', 'Отменено курьером', head_format)

    worksheet.write('G5', 'кол-во', head_format)
    worksheet.write('H5', 'на сумму', head_format)
    worksheet.write('I5', 'кол-во', head_format)
    worksheet.write('J5', 'на сумму', head_format)
    worksheet.write('K5', 'кол-во', head_format)
    worksheet.write('L5', 'на сумму', head_format)
    worksheet.write('M5', 'кол-во', head_format)
    worksheet.write('N5', 'на сумму', head_format)
    worksheet.write('O5', 'кол-во', head_format)
    worksheet.write('P5', 'на сумму', head_format)

    worksheet.write('R4', 'Точка продаж (бонусные)', head_format)
    worksheet.set_column(17, 17, 40)
    worksheet.set_column(18, 21, 25)
    worksheet.write('S4', 'Всего', head_format)
    worksheet.write('T4', 'Выполнено', head_format)
    worksheet.write('U4', 'Отменено покупателем', head_format)
    worksheet.write('V4', 'Отменено продавцом', head_format)


def head_orders_admin(worksheet, head_format):
    """Шапка второго листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.set_column(4, 4, 30)
    worksheet.merge_range('F2:F3', 'Локация\nдоставки', head_format)
    worksheet.set_column(5, 5, 30)
    worksheet.merge_range('G2:G3', 'ID\nпродавца', head_format)
    worksheet.merge_range('H2:H3', 'ID\nкурьера', head_format)
    worksheet.merge_range('I2:I3', 'ID\nклиента', head_format)
    worksheet.merge_range('J2:J3', 'Дата\nзаказа', head_format)
    worksheet.merge_range('K2:K3', 'Время\nзаказа', head_format)
    worksheet.merge_range('L2:L3', 'Доставить\nчерез\n(мин)', head_format)
    worksheet.merge_range('M2:M3', 'Время\nпринятия\nзаказа', head_format)
    worksheet.merge_range('N2:N3', 'Время\nдоставки\nзаказа', head_format)
    worksheet.merge_range('O2:O3', 'Время\nотмены\nзаказа', head_format)
    worksheet.merge_range('P2:P3', '№\nзаказа', head_format)
    worksheet.set_column(6, 14, 10)
    worksheet.set_column(15, 15, 8)
    worksheet.merge_range('Q2:Q3', 'Заказанные позиции', head_format)
    worksheet.set_column(16, 16, 30)
    worksheet.merge_range('R2:R3', 'Кол-во', head_format)
    worksheet.merge_range('S2:S3', 'Цена\nза ед.\n(руб)', head_format)
    worksheet.merge_range('T2:T3', 'Сумма\nзаказа\n(руб)', head_format)
    worksheet.set_column(17, 18, 10)
    worksheet.merge_range('U2:U3', 'Метод\nдоставки', head_format)
    worksheet.set_column(20, 20, 13)
    worksheet.merge_range('V2:V3', 'Статус\nзаказа', head_format)
    worksheet.set_column(21, 21, 20)
    worksheet.merge_range('W2:W3', 'Отзыв\nклиента', head_format)
    worksheet.merge_range('X2:X3', 'Причина\nотмены', head_format)
    worksheet.set_column(22, 23, 30)


def head_bonus_orders_admin(worksheet, head_format):
    """Шапка третьего листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)  # 4
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.set_column(4, 4, 30)
    worksheet.merge_range('F2:F3', 'ID\nпродавца', head_format)
    worksheet.set_column(5, 13, 10)
    worksheet.merge_range('G2:G3', 'ID\nклиента', head_format)
    worksheet.merge_range('H2:H3', 'Дата\nзаказа', head_format)
    worksheet.merge_range('I2:I3', 'Время\nзаказа', head_format)
    worksheet.merge_range('J2:J3', 'Время\nпринятия\nзаказа', head_format)
    worksheet.merge_range('K2:K3', 'Время\nвыдачи\nзаказа', head_format)
    worksheet.merge_range('L2:L3', 'Время\nотмены\nзаказа', head_format)
    worksheet.merge_range('M2:M3', '№\nзаказа', head_format)
    worksheet.merge_range('N2:N3', 'Кол-во', head_format)
    worksheet.merge_range('O2:O3', 'Статус\nзаказа', head_format)
    worksheet.set_column(14, 14, 20)
    worksheet.merge_range('P2:P3', 'Отзыв\nклиента', head_format)
    worksheet.merge_range('Q2:Q3', 'Причина\nотмены', head_format)
    worksheet.set_column(15, 16, 30)


def head_sellers_admin(worksheet, head_format):
    """Шапка четвертого листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 6, 15)
    worksheet.set_column(7, 7, 25)
    worksheet.set_column(8, 8, 15)
    worksheet.set_column(9, 9, 10)
    worksheet.set_column(10, 10, 15)
    worksheet.set_column(11, 11, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.merge_range('F2:F3', 'ID\nпродавца', head_format)
    worksheet.merge_range('G2:G3', 'telegramID\nпродавца', head_format)
    worksheet.merge_range('H2:H3', 'Имя продавца', head_format)
    worksheet.merge_range('I2:J2', 'Заказы', head_format)
    worksheet.write('I3', 'наименование', head_format)
    worksheet.write('J3', 'кол-во', head_format)
    worksheet.merge_range('K2:L2', 'Бонусные аказы', head_format)
    worksheet.write('K3', 'наименование', head_format)
    worksheet.write('L3', 'кол-во', head_format)


def head_couriers_admin(worksheet, head_format):
    """Шапка пятого листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 6, 15)
    worksheet.set_column(7, 7, 25)
    worksheet.set_column(8, 8, 15)
    worksheet.set_column(9, 9, 10)
    worksheet.set_column(10, 10, 15)
    worksheet.set_column(11, 11, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.merge_range('F2:F3', 'ID\nкурьера', head_format)
    worksheet.merge_range('G2:G3', 'telegramID\nкурьера', head_format)
    worksheet.merge_range('H2:H3', 'Имя курьера', head_format)
    worksheet.merge_range('I2:J2', 'Заказы', head_format)
    worksheet.write('I3', 'наименование', head_format)
    worksheet.write('J3', 'кол-во', head_format)


def head_clients_admin(worksheet, head_format):
    """Шапка шестого листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 6, 15)
    worksheet.set_column(7, 7, 15)
    worksheet.set_column(8, 8, 10)
    worksheet.set_column(9, 9, 15)
    worksheet.set_column(10, 10, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.merge_range('F2:F3', 'ID\nклиента', head_format)
    worksheet.merge_range('G2:G3', 'telegramID\nклиента', head_format)
    worksheet.merge_range('H2:I2', 'Заказы', head_format)
    worksheet.write('H3', 'наименование', head_format)
    worksheet.write('I3', 'кол-во', head_format)
    worksheet.merge_range('J2:K2', 'Бонусные аказы', head_format)
    worksheet.write('J3', 'наименование', head_format)
    worksheet.write('K3', 'кол-во', head_format)


def body_indicators_admin(worksheet, body_format, indicators, bonus_indicators, indicators_by_loc,
                          bonus_indicators_by_loc):
    """Записываем показатели"""
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

    if bonus_indicators:
        worksheet.write('C14', f'{bonus_indicators["all_orders"]}', body_format)
        worksheet.write('C15', f'{bonus_indicators["completed"]}', body_format)
        worksheet.write('C16', f'{bonus_indicators["canceled_by_client"]}', body_format)
        worksheet.write('C17', f'{bonus_indicators["canceled_by_seller"]}', body_format)

    if indicators_by_loc:
        first_line = 6
        for ind in indicators_by_loc:
            worksheet.write(f'F{first_line}', f"{ind['location_name']}", body_format)
            worksheet.write(f'G{first_line}', f"{ind['all_orders']}", body_format)
            worksheet.write(f'H{first_line}', f"{ind['all_orders_price']}", body_format)
            worksheet.write(f'I{first_line}', f"{ind['completed']}", body_format)
            worksheet.write(f'J{first_line}', f"{ind['completed_price']}", body_format)
            worksheet.write(f'K{first_line}', f"{ind['canceled_by_client']}", body_format)
            worksheet.write(f'L{first_line}', f"{ind['canceled_by_client_price']}", body_format)
            worksheet.write(f'M{first_line}', f"{ind['canceled_by_seller']}", body_format)
            worksheet.write(f'N{first_line}', f"{ind['canceled_by_seller_price']}", body_format)
            worksheet.write(f'O{first_line}', f"{ind['canceled_by_courier']}", body_format)
            worksheet.write(f'P{first_line}', f"{ind['canceled_by_courier_price']}", body_format)
            first_line += 1

    if bonus_indicators_by_loc:
        first_line = 5
        for ind in bonus_indicators_by_loc:
            worksheet.write(f'R{first_line}', f"{ind['location_name']}", body_format)
            worksheet.write(f'S{first_line}', f"{ind['all_orders']}", body_format)
            worksheet.write(f'T{first_line}', f"{ind['completed']}", body_format)
            worksheet.write(f'U{first_line}', f"{ind['canceled_by_client']}", body_format)
            worksheet.write(f'V{first_line}', f"{ind['canceled_by_seller']}", body_format)
            first_line += 1


def body_orders_admin(worksheet, body_format, orders, start_period, end_period):
    """Записываем заказы"""
    if orders:
        for order in orders:
            if len(order['order_products']) > 1:
                worksheet.merge_range(f'B{order["first_line"]}:B{order["last_line"]}', f'{order["num"]}', body_format)
                worksheet.merge_range(f'C{order["first_line"]}:C{order["last_line"]}', f'{start_period}', body_format)
                worksheet.merge_range(f'D{order["first_line"]}:D{order["last_line"]}', f'{end_period}', body_format)
                worksheet.merge_range(f'E{order["first_line"]}:E{order["last_line"]}', f'{order["location_name"]}',
                                      body_format)
                worksheet.merge_range(f'F{order["first_line"]}:F{order["last_line"]}', f'{order["local_object_name"]}',
                                      body_format)
                if order["order_seller_id"]:
                    worksheet.merge_range(f'G{order["first_line"]}:G{order["last_line"]}',
                                          f'{order["order_seller_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'G{order["first_line"]}:G{order["last_line"]}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.merge_range(f'H{order["first_line"]}:H{order["last_line"]}',
                                          f'{order["order_courier_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'H{order["first_line"]}:H{order["last_line"]}', f'', body_format)
                worksheet.merge_range(f'I{order["first_line"]}:I{order["last_line"]}', f'{order["order_user_id"]}',
                                      body_format)
                worksheet.merge_range(f'J{order["first_line"]}:J{order["last_line"]}',
                                      f'{order["order_date"].strftime("%d.%m.%Y")}',
                                      body_format)
                worksheet.merge_range(f'K{order["first_line"]}:K{order["last_line"]}',
                                      f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                      body_format)
                worksheet.merge_range(f'L{order["first_line"]}:L{order["last_line"]}',
                                      f'{order["order_deliver_through"]}',
                                      body_format)
                if order["order_accepted_at"]:
                    worksheet.merge_range(f'M{order["first_line"]}:M{order["last_line"]}',
                                          f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'M{order["first_line"]}:M{order["last_line"]}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}',
                                          f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.merge_range(f'O{order["first_line"]}:O{order["last_line"]}',
                                          f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'O{order["first_line"]}:O{order["last_line"]}', f'', body_format)
                worksheet.merge_range(f'P{order["first_line"]}:P{order["last_line"]}', f'{order["order_id"]}',
                                      body_format)
                worksheet.merge_range(f'T{order["first_line"]}:T{order["last_line"]}', f'{order["order_final_price"]}',
                                      body_format)
                worksheet.merge_range(f'U{order["first_line"]}:U{order["last_line"]}',
                                      f'{order["order_delivery_method"]}',
                                      body_format)
                worksheet.merge_range(f'V{order["first_line"]}:V{order["last_line"]}', f'{order["order_status"]}',
                                      body_format)
                if order["order_review"]:
                    worksheet.merge_range(f'W{order["first_line"]}:W{order["last_line"]}', f'{order["order_review"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'W{order["first_line"]}:W{order["last_line"]}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.merge_range(f'X{order["first_line"]}:X{order["last_line"]}',
                                          f'{order["order_reason_for_rejection"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'X{order["first_line"]}:X{order["last_line"]}', f'', body_format)
                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'S{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1
            else:
                worksheet.write(f'B{order["first_line"]}', f'{order["num"]}', body_format)
                worksheet.write(f'C{order["first_line"]}', f'{start_period}', body_format)
                worksheet.write(f'D{order["first_line"]}', f'{end_period}', body_format)
                worksheet.write(f'E{order["first_line"]}', f'{order["location_name"]}', body_format)
                worksheet.write(f'F{order["first_line"]}', f'{order["local_object_name"]}', body_format)
                if order["order_seller_id"]:
                    worksheet.write(f'G{order["first_line"]}', f'{order["order_seller_id"]}', body_format)
                else:
                    worksheet.write(f'G{order["first_line"]}', f'', body_format)
                if order["order_courier_id"]:
                    worksheet.write(f'H{order["first_line"]}', f'{order["order_courier_id"]}', body_format)
                else:
                    worksheet.write(f'H{order["first_line"]}', f'', body_format)
                worksheet.write(f'I{order["first_line"]}', f'{order["order_user_id"]}', body_format)
                worksheet.write(f'J{order["first_line"]}', f'{order["order_date"].strftime("%d.%m.%Y")}',
                                body_format)
                worksheet.write(f'K{order["first_line"]}', f'{order["order_created_at"].strftime("%H:%M:%S")}',
                                body_format)
                worksheet.write(f'L{order["first_line"]}', f'{order["order_deliver_through"]}', body_format)
                if order["order_accepted_at"]:
                    worksheet.write(f'M{order["first_line"]}', f'{order["order_accepted_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'M{order["first_line"]}', f'', body_format)
                if order["order_delivered_at"]:
                    worksheet.write(f'N{order["first_line"]}', f'{order["order_delivered_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'N{order["first_line"]}', f'', body_format)
                if order["order_canceled_at"]:
                    worksheet.write(f'O{order["first_line"]}', f'{order["order_canceled_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'O{order["first_line"]}', f'', body_format)
                worksheet.write(f'P{order["first_line"]}', f'{order["order_id"]}', body_format)
                worksheet.write(f'T{order["first_line"]}', f'{order["order_final_price"]}', body_format)
                worksheet.write(f'U{order["first_line"]}', f'{order["order_delivery_method"]}', body_format)
                worksheet.write(f'V{order["first_line"]}', f'{order["order_status"]}', body_format)
                if order["order_review"]:
                    worksheet.write(f'W{order["first_line"]}', f'{order["order_review"]}', body_format)
                else:
                    worksheet.write(f'W{order["first_line"]}', f'', body_format)
                if order["order_reason_for_rejection"]:
                    worksheet.write(f'X{order["first_line"]}', f'{order["order_reason_for_rejection"]}',
                                    body_format)
                else:
                    worksheet.write(f'X{order["first_line"]}', f'', body_format)
                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'Q{first_prod_line}', f'{prod["op_product_name"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["op_quantity"]}', body_format)
                    worksheet.write(f'S{first_prod_line}', f'{prod["op_price_per_unit"]}', body_format)
                    first_prod_line += 1


def body_bonus_orders_admin(worksheet, body_format, orders, start_period, end_period):
    """Записываем бонусные заказы"""
    first_string = 4
    num = 1
    if orders:
        for order in orders:
            worksheet.write(f'B{first_string}', f'{num}', body_format)
            worksheet.write(f'C{first_string}', f'{start_period}', body_format)
            worksheet.write(f'D{first_string}', f'{end_period}', body_format)
            worksheet.write(f'E{first_string}', f'{order["location_name"]}', body_format)
            if order["bonus_order_seller_id"]:
                worksheet.write(f'F{first_string}', f'{order["bonus_order_seller_id"]}', body_format)
            else:
                worksheet.write(f'F{first_string}', f'', body_format)
            worksheet.write(f'G{first_string}', f'{order["bonus_order_user_id"]}', body_format)
            worksheet.write(f'H{first_string}', f'{order["bonus_order_date"].strftime("%d.%m.%Y")}',
                            body_format)
            worksheet.write(f'I{first_string}', f'{order["bonus_order_created_at"].strftime("%H:%M:%S")}',
                            body_format)
            if order["bonus_order_accepted_at"]:
                worksheet.write(f'J{first_string}', f'{order["bonus_order_accepted_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'J{first_string}', f'', body_format)
            if order["bonus_order_delivered_at"]:
                worksheet.write(f'K{first_string}', f'{order["bonus_order_delivered_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'K{first_string}', f'', body_format)
            if order["bonus_order_canceled_at"]:
                worksheet.write(f'L{first_string}', f'{order["bonus_order_canceled_at"].strftime("%H:%M:%S")}',
                                body_format)
            else:
                worksheet.write(f'L{first_string}', f'', body_format)
            worksheet.write(f'M{first_string}', f'{order["bonus_order_id"]}', body_format)
            worksheet.write(f'N{first_string}', f'{order["bonus_order_quantity"]}', body_format)
            worksheet.write(f'O{first_string}', f'{order["bonus_order_status"]}', body_format)
            if order["bonus_order_review"]:
                worksheet.write(f'P{first_string}', f'{order["bonus_order_review"]}', body_format)
            else:
                worksheet.write(f'P{first_string}', f'', body_format)
            if order["bonus_order_reason_for_rejection"]:
                worksheet.write(f'Q{first_string}', f'{order["bonus_order_reason_for_rejection"]}',
                                body_format)
            else:
                worksheet.write(f'Q{first_string}', f'', body_format)
            first_string += 1
            num += 1


def body_sellers_admin(worksheet, body_format, sellers, start_period, end_period):
    """Записываем продавцов"""
    if sellers:
        first_string = 4
        num = 1
        for seller in sellers:

            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{seller["location_name"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{seller["order_seller_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{seller["seller_telegram_id"]}', body_format)
            worksheet.merge_range(f'H{first_string}:H{ls}', f'{seller["seller_name"]}', body_format)
            worksheet.write(f'I{first_string}', f'Всего', body_format)
            worksheet.write(f'J{first_string}', f'{seller["all_orders"]}', body_format)
            worksheet.write(f'I{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'J{first_string + 1}', f'{seller["completed_orders"]}', body_format)
            worksheet.write(f'I{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'J{first_string + 2}', f'{seller["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'I{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'J{first_string + 3}', f'{seller["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'I{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'J{first_string + 4}', f'{seller["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'Выполнено', body_format)
            worksheet.write(f'K{first_string + 4}', f'Отменено', body_format)
            if 'all_bonus_orders' in seller:
                worksheet.merge_range(f'L{first_string}:L{first_string + 1}', f'{seller["all_bonus_orders"]}',
                                      body_format)
                worksheet.merge_range(f'L{first_string + 2}:L{first_string + 3}', f'{seller["completed_bonus_orders"]}',
                                      body_format)
                worksheet.write(f'L{first_string + 4}', f'{seller["canceled_bonus_orders"]}', body_format)
            else:
                worksheet.merge_range(f'L{first_string}:L{first_string + 1}', f'', body_format)
                worksheet.merge_range(f'L{first_string + 2}:L{first_string + 3}', f'', body_format)
                worksheet.write(f'L{first_string + 4}', f'', body_format)

            first_string += 5
            num += 1


def body_couriers_admin(worksheet, body_format, couriers, start_period, end_period):
    """Записываем курьеров"""
    if couriers:
        first_string = 4
        num = 1
        for courier in couriers:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{courier["location_name"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{courier["order_courier_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{courier["courier_telegram_id"]}', body_format)
            worksheet.merge_range(f'H{first_string}:H{ls}', f'{courier["courier_name"]}', body_format)
            worksheet.write(f'I{first_string}', f'Всего', body_format)
            worksheet.write(f'J{first_string}', f'{courier["all_orders"]}', body_format)
            worksheet.write(f'I{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'J{first_string + 1}', f'{courier["completed_orders"]}', body_format)
            worksheet.write(f'I{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'J{first_string + 2}', f'{courier["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'I{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'J{first_string + 3}', f'{courier["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'I{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'J{first_string + 4}', f'{courier["canceled_by_client_orders"]}', body_format)
            first_string += 5
            num += 1


def body_clients_admin(worksheet, body_format, clients, start_period, end_period):
    """Записываем клиентов"""
    if clients:
        first_string = 4
        num = 1
        for client in clients:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{client["location_name"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{client["order_user_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{client["user_telegram_id"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{client["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{client["completed_orders"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено продавцом', body_format)
            worksheet.write(f'I{first_string + 2}', f'{client["canceled_by_seller_orders"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено курьером', body_format)
            worksheet.write(f'I{first_string + 3}', f'{client["canceled_by_courier_orders"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'Отменено пользователем', body_format)
            worksheet.write(f'I{first_string + 4}', f'{client["canceled_by_client_orders"]}', body_format)

            worksheet.merge_range(f'J{first_string}:J{first_string + 1}', f'Всего', body_format)
            worksheet.merge_range(f'J{first_string + 2}:J{first_string + 3}', f'Выполнено', body_format)
            worksheet.write(f'J{first_string + 4}', f'Отменено', body_format)
            if "all_bonus_orders" in client:
                worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'{client["all_bonus_orders"]}',
                                      body_format)
                worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'{client["completed_bonus_orders"]}',
                                      body_format)
                worksheet.write(f'K{first_string + 4}', f'{client["canceled_bonus_orders"]}', body_format)
            else:
                worksheet.merge_range(f'K{first_string}:K{first_string + 1}', f'', body_format)
                worksheet.merge_range(f'K{first_string + 2}:K{first_string + 3}', f'', body_format)
                worksheet.write(f'K{first_string + 4}', f'', body_format)

            first_string += 5
            num += 1


def write_admin_statistics(data):
    """Записываем статистику"""
    orders = get_orders(data['orders'], data['products'], data['numbers'])

    users = get_users_indicators(data['user_orders'], data['user_bonus_orders'])

    sellers = get_sellers_indicators(data['sellers_orders'], data['sellers_bonus'])

    threads = []

    workbook = xlsxwriter.Workbook(data['path'])

    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet1 = workbook.add_worksheet('Показатели за период')
    worksheet2 = workbook.add_worksheet('Статистика заказов')
    worksheet3 = workbook.add_worksheet('Статистика бонусных заказов')
    worksheet4 = workbook.add_worksheet('Продавцы')
    worksheet5 = workbook.add_worksheet('Курьеры')
    worksheet6 = workbook.add_worksheet('Клиенты')

    o = threading.Thread(target=body_orders_admin, args=(worksheet2, body_format, orders,
                                                         data['first_period'].strftime("%d.%m.%Y"),
                                                         data['end_period'].strftime("%d.%m.%Y")))
    o.start()
    threads.append(o)

    b = threading.Thread(target=body_bonus_orders_admin,
                         args=(worksheet3, body_format, data['bonus_orders'], data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    b.start()
    threads.append(b)

    u = threading.Thread(target=body_clients_admin,
                         args=(worksheet6, body_format, users, data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    u.start()
    threads.append(u)

    i = threading.Thread(target=body_indicators_admin, args=(worksheet1, body_format, data['indicators'],
                                                             data['bonus_indicators'], data['indicators_by_loc'],
                                                             data['bonus_indicators_by_loc']))
    i.start()
    threads.append(i)

    s = threading.Thread(target=body_sellers_admin,
                         args=(worksheet4, body_format, sellers, data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    s.start()
    threads.append(s)

    c = threading.Thread(target=body_couriers_admin,
                         args=(worksheet5, body_format, data['couriers_orders'],
                               data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    c.start()
    threads.append(c)

    head_indicators_admin(worksheet1, head_format, body_format)
    head_orders_admin(worksheet2, head_format)
    head_bonus_orders_admin(worksheet3, head_format)
    head_sellers_admin(worksheet4, head_format)
    head_couriers_admin(worksheet5, head_format)
    head_clients_admin(worksheet6, head_format)

    for x in threads:
        x.join()
    workbook.close()
    try:
        send_email(data['file_name'], data['file_name'], data['to_email'], data['path'], data['file_name'])

        os.remove(data['path'])
        return True
    except Exception as err:
        os.remove(data['path'])
        logging.error(err)
        return False


def head_delivery_indicators_admin(worksheet, head_format, body_format):
    """Шапка для первого листа"""
    worksheet.set_column(0, 0, 1)

    worksheet.write('B4', 'Показатели за период', head_format)
    worksheet.set_column(1, 1, 40)
    worksheet.write('C4', 'Кол-во', head_format)
    worksheet.set_column(2, 2, 20)
    worksheet.write('D4', 'На сумму (руб)', head_format)
    worksheet.set_column(3, 3, 20)
    worksheet.write('B5', 'Всего заказов', body_format)
    worksheet.write('B6', 'в т.ч. Выполнено', body_format)
    worksheet.write('B7', 'в т.ч. В обработке', body_format)
    worksheet.write('B8', 'в т.ч. Еще не принят', body_format)
    worksheet.write('B9', 'в т.ч. Отменен поставщиком', body_format)
    worksheet.write('B10', 'в т.ч. Отменен заказчиком', body_format)

    worksheet.merge_range('F4:F5', 'Точка продаж', head_format)
    worksheet.set_column(5, 5, 40)
    worksheet.set_column(6, 17, 13)
    worksheet.merge_range('G4:H4', 'Всего', head_format)
    worksheet.merge_range('I4:J4', 'Выполнено', head_format)
    worksheet.merge_range('K4:L4', 'В обработке', head_format)
    worksheet.merge_range('M4:N4', 'Еще не принят', head_format)
    worksheet.merge_range('O4:P4', 'Отменен поставщиком', head_format)
    worksheet.merge_range('Q4:R4', 'Отменен заказчиком', head_format)

    worksheet.write('G5', 'кол-во', head_format)
    worksheet.write('H5', 'на сумму', head_format)
    worksheet.write('I5', 'кол-во', head_format)
    worksheet.write('J5', 'на сумму', head_format)
    worksheet.write('K5', 'кол-во', head_format)
    worksheet.write('L5', 'на сумму', head_format)
    worksheet.write('M5', 'кол-во', head_format)
    worksheet.write('N5', 'на сумму', head_format)
    worksheet.write('O5', 'кол-во', head_format)
    worksheet.write('P5', 'на сумму', head_format)
    worksheet.write('Q5', 'кол-во', head_format)
    worksheet.write('R5', 'на сумму', head_format)


def head_delivery_orders_admin(worksheet, head_format):
    """Шапка второго листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.set_column(4, 4, 30)
    worksheet.merge_range('F2:F3', 'ID\nпоставщика', head_format)  #####
    worksheet.merge_range('G2:G3', 'ID\nзаказчика', head_format)
    worksheet.merge_range('H2:H3', 'ID\nкурьера', head_format)
    worksheet.merge_range('I2:I3', 'Дата\nзаказа', head_format)
    worksheet.merge_range('J2:J3', 'Дата\nотмены заказа', head_format)
    worksheet.merge_range('K2:K3', 'Дата последнего\nизменения заказа', head_format)
    worksheet.merge_range('L2:L3', 'Дата\nдоставки', head_format)
    worksheet.merge_range('M2:M3', 'Время\nдоставки', head_format)
    worksheet.merge_range('N2:N3', 'Доставлен в', head_format)
    worksheet.merge_range('O2:O3', '№\nзаказа', head_format)
    worksheet.merge_range('P2:P3', 'Заказанные позиции', head_format)
    worksheet.set_column(5, 5, 12)
    worksheet.set_column(6, 7, 10)
    worksheet.set_column(8, 13, 20)
    worksheet.set_column(14, 14, 8)
    worksheet.merge_range('Q2:Q3', 'Кол-во', head_format)
    worksheet.set_column(15, 15, 30)
    worksheet.merge_range('R2:R3', 'Цена\nза ед.\n(руб)', head_format)
    worksheet.merge_range('S2:S3', 'Сумма\nзаказа\n(руб)', head_format)
    worksheet.merge_range('T2:T3', 'Статус\nзаказа', head_format)
    worksheet.set_column(16, 19, 10)
    worksheet.set_column(19, 19, 25)


def head_delivery_sellers_admin(worksheet, head_format):
    """Шапка четвертого листа"""
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
    worksheet.merge_range('E2:E3', 'ID\nпоставщика', head_format)
    worksheet.merge_range('F2:F3', 'telegramID\nпоставщика', head_format)
    worksheet.merge_range('G2:G3', 'Имя поставщика', head_format)
    worksheet.merge_range('H2:I2', 'Заказы', head_format)
    worksheet.write('H3', 'наименование', head_format)
    worksheet.write('I3', 'кол-во', head_format)


def head_delivery_couriers(worksheet, head_format):
    """Шапка пятого листа"""
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


def head_delivery_clients_admin(worksheet, head_format):
    """Шапка шестого листа"""
    worksheet.set_column(0, 0, 1)
    worksheet.set_row(1, 30)
    worksheet.set_row(2, 30)
    worksheet.merge_range('B2:B3', '№', head_format)
    worksheet.set_column(1, 1, 8)
    worksheet.merge_range('C2:D2', 'Период', head_format)
    worksheet.set_column(2, 3, 10)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 6, 15)
    worksheet.set_column(7, 7, 30)
    worksheet.set_column(8, 9, 15)
    worksheet.write('C3', 'с', head_format)
    worksheet.write('D3', 'по', head_format)
    worksheet.merge_range('E2:E3', 'Точка\nпродаж', head_format)
    worksheet.merge_range('F2:F3', 'ID\nклиента', head_format)
    worksheet.merge_range('G2:G3', 'telegramID\nклиента', head_format)
    worksheet.merge_range('H2:H3', 'Имя\nклиента', head_format)
    worksheet.merge_range('I2:J2', 'Заказы', head_format)
    worksheet.write('I3', 'наименование', head_format)
    worksheet.write('J3', 'кол-во', head_format)


def body_delivery_indicators_admin(worksheet, body_format, indicators, indicators_by_loc):
    """Записываем показатели"""
    if indicators:
        worksheet.write('C5', f'{indicators["all_orders"]}', body_format)
        worksheet.write('C6', f'{indicators["completed"]}', body_format)
        worksheet.write('C7', f'{indicators["waitings"]}', body_format)
        worksheet.write('C8', f'{indicators["wait_confirm"]}', body_format)
        worksheet.write('C9', f'{indicators["canceled_by_seller"]}', body_format)
        worksheet.write('C10', f'{indicators["canceled_by_client"]}', body_format)

        worksheet.write('D5', f'{indicators["all_orders_price"]}', body_format)
        worksheet.write('D6', f'{indicators["completed_price"]}', body_format)
        worksheet.write('D7', f'{indicators["waitings_price"]}', body_format)
        worksheet.write('D8', f'{indicators["wait_confirm_price"]}', body_format)
        worksheet.write('D9', f'{indicators["canceled_by_seller_price"]}', body_format)
        worksheet.write('D10', f'{indicators["canceled_by_client_price"]}', body_format)

    if indicators_by_loc:
        first_line = 6
        for ind in indicators_by_loc:
            worksheet.write(f'F{first_line}', f"{ind['location_name']}", body_format)
            worksheet.write(f'G{first_line}', f"{ind['all_orders']}", body_format)
            worksheet.write(f'H{first_line}', f"{ind['all_orders_price']}", body_format)
            worksheet.write(f'I{first_line}', f"{ind['completed']}", body_format)
            worksheet.write(f'J{first_line}', f"{ind['completed_price']}", body_format)
            worksheet.write(f'K{first_line}', f"{ind['waitings']}", body_format)
            worksheet.write(f'L{first_line}', f"{ind['waitings_price']}", body_format)
            worksheet.write(f'M{first_line}', f"{ind['wait_confirm']}", body_format)
            worksheet.write(f'N{first_line}', f"{ind['wait_confirm_price']}", body_format)
            worksheet.write(f'O{first_line}', f"{ind['canceled_by_seller']}", body_format)
            worksheet.write(f'P{first_line}', f"{ind['canceled_by_seller_price']}", body_format)
            worksheet.write(f'Q{first_line}', f"{ind['canceled_by_client']}", body_format)
            worksheet.write(f'R{first_line}', f"{ind['canceled_by_client_price']}", body_format)
            first_line += 1


def body_delivery_orders_admin(worksheet, body_format, orders, start_period, end_period):
    """Записываем заказы"""
    if orders:
        for order in orders:
            if len(order['order_products']) > 1:
                worksheet.merge_range(f'B{order["first_line"]}:B{order["last_line"]}', f'{order["num"]}', body_format)
                worksheet.merge_range(f'C{order["first_line"]}:C{order["last_line"]}', f'{start_period}', body_format)
                worksheet.merge_range(f'D{order["first_line"]}:D{order["last_line"]}', f'{end_period}', body_format)
                worksheet.merge_range(f'E{order["first_line"]}:E{order["last_line"]}', f'{order["location_name"]}',
                                      body_format)
                if order["delivery_order_admin_id"]:
                    worksheet.merge_range(f'F{order["first_line"]}:F{order["last_line"]}',
                                          f'{order["delivery_order_admin_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'F{order["first_line"]}:F{order["last_line"]}', f'', body_format)

                worksheet.merge_range(f'G{order["first_line"]}:G{order["last_line"]}',
                                      f'{order["delivery_order_seller_admin_id"]}',
                                      body_format)

                if order["delivery_order_courier_id"]:
                    worksheet.merge_range(f'H{order["first_line"]}:H{order["last_line"]}',
                                          f'{order["delivery_order_courier_id"]}',
                                          body_format)
                else:
                    worksheet.merge_range(f'H{order["first_line"]}:H{order["last_line"]}', f'', body_format)

                worksheet.merge_range(f'I{order["first_line"]}:I{order["last_line"]}',
                                      f'{order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}',
                                      body_format)
                if order['delivery_order_canceled_at']:
                    worksheet.merge_range(f'J{order["first_line"]}:J{order["last_line"]}',
                                          f'{order["delivery_order_canceled_at"].strftime("%d.%m.%Y %H:%M")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'J{order["first_line"]}:J{order["last_line"]}', f'', body_format)

                if order['delivery_order_changed_at']:
                    worksheet.merge_range(f'K{order["first_line"]}:K{order["last_line"]}',
                                          f'{order["delivery_order_changed_at"].strftime("%d.%m.%Y %H:%M")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'K{order["first_line"]}:K{order["last_line"]}', f'', body_format)

                worksheet.merge_range(f'L{order["first_line"]}:L{order["last_line"]}',
                                      f'{order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")}',
                                      body_format)
                worksheet.merge_range(f'M{order["first_line"]}:M{order["last_line"]}',
                                      f'{order["delivery_order_time_info"]}',
                                      body_format)

                if order["delivery_order_delivered_at"]:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}',
                                          f'{order["delivery_order_delivered_at"].strftime("%H:%M:%S")}',
                                          body_format)
                else:
                    worksheet.merge_range(f'N{order["first_line"]}:N{order["last_line"]}', f'', body_format)

                worksheet.merge_range(f'O{order["first_line"]}:O{order["last_line"]}',
                                      f'{order["delivery_order_id"]}',
                                      body_format)

                worksheet.merge_range(f'S{order["first_line"]}:S{order["last_line"]}',
                                      f'{order["delivery_order_final_price"]}',
                                      body_format)
                worksheet.merge_range(f'T{order["first_line"]}:T{order["last_line"]}',
                                      f'{order["delivery_order_status"]}',
                                      body_format)

                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'P{first_prod_line}', f'{prod["dop_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["dop_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["dop_price_per_unit"]}', body_format)
                    first_prod_line += 1
            else:
                worksheet.write(f'B{order["first_line"]}', f'{order["num"]}', body_format)
                worksheet.write(f'C{order["first_line"]}', f'{start_period}', body_format)
                worksheet.write(f'D{order["first_line"]}', f'{end_period}', body_format)
                worksheet.write(f'E{order["first_line"]}', f'{order["location_name"]}', body_format)

                if order["delivery_order_admin_id"]:
                    worksheet.write(f'F{order["first_line"]}',
                                    f'{order["delivery_order_admin_id"]}',
                                    body_format)
                else:
                    worksheet.write(f'F{order["first_line"]}', f'', body_format)

                worksheet.write(f'G{order["first_line"]}',
                                f'{order["delivery_order_seller_admin_id"]}',
                                body_format)

                if order["delivery_order_courier_id"]:
                    worksheet.write(f'H{order["first_line"]}',
                                    f'{order["delivery_order_courier_id"]}',
                                    body_format)
                else:
                    worksheet.write(f'H{order["first_line"]}', f'', body_format)

                worksheet.write(f'I{order["first_line"]}',
                                f'{order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}',
                                body_format)
                if order['delivery_order_canceled_at']:
                    worksheet.write(f'J{order["first_line"]}',
                                    f'{order["delivery_order_canceled_at"].strftime("%d.%m.%Y %H:%M")}',
                                    body_format)
                else:
                    worksheet.write(f'J{order["first_line"]}', f'', body_format)

                if order['delivery_order_changed_at']:
                    worksheet.write(f'K{order["first_line"]}',
                                    f'{order["delivery_order_changed_at"].strftime("%d.%m.%Y %H:%M")}',
                                    body_format)
                else:
                    worksheet.write(f'K{order["first_line"]}', f'', body_format)

                worksheet.write(f'L{order["first_line"]}',
                                f'{order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")}',
                                body_format)
                worksheet.write(f'M{order["first_line"]}',
                                f'{order["delivery_order_time_info"]}',
                                body_format)

                if order["delivery_order_delivered_at"]:
                    worksheet.write(f'N{order["first_line"]}',
                                    f'{order["delivery_order_delivered_at"].strftime("%H:%M:%S")}',
                                    body_format)
                else:
                    worksheet.write(f'N{order["first_line"]}', f'', body_format)

                worksheet.write(f'O{order["first_line"]}',
                                f'{order["delivery_order_id"]}',
                                body_format)

                worksheet.write(f'S{order["first_line"]}',
                                f'{order["delivery_order_final_price"]}',
                                body_format)
                worksheet.write(f'T{order["first_line"]}',
                                f'{order["delivery_order_status"]}',
                                body_format)
                first_prod_line = order["first_line"]
                for prod in order['order_products']:
                    worksheet.write(f'P{first_prod_line}', f'{prod["dop_product_name"]}', body_format)
                    worksheet.write(f'Q{first_prod_line}', f'{prod["dop_quantity"]}', body_format)
                    worksheet.write(f'R{first_prod_line}', f'{prod["dop_price_per_unit"]}', body_format)
                    first_prod_line += 1


def body_delivery_sellers_admin(worksheet, body_format, sellers, start_period, end_period):
    """Записываем продавцов"""
    if sellers:
        first_string = 4
        num = 1
        for seller in sellers:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{seller["delivery_order_admin_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{seller["admin_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{seller["admin_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{seller["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{seller["completed"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено поставщиком', body_format)
            worksheet.write(f'I{first_string + 2}', f'{seller["canceled_by_seller"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено заказчиком', body_format)
            worksheet.write(f'I{first_string + 3}', f'{seller["canceled_by_client"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'В процессе', body_format)
            worksheet.write(f'I{first_string + 4}', f'{seller["waitings"]}', body_format)
            first_string += 5
            num += 1


def body_delivery_couriers(worksheet, body_format, couriers, start_period, end_period):
    """Записываем курьеров"""
    if couriers:
        first_string = 4
        num = 1
        for courier in couriers:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{courier["delivery_order_courier_id"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{courier["delivery_courier_telegram_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{courier["delivery_courier_name"]}', body_format)
            worksheet.write(f'H{first_string}', f'Всего', body_format)
            worksheet.write(f'I{first_string}', f'{courier["all_orders"]}', body_format)
            worksheet.write(f'H{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'I{first_string + 1}', f'{courier["completed"]}', body_format)
            worksheet.write(f'H{first_string + 2}', f'Отменено поставщиком', body_format)
            worksheet.write(f'I{first_string + 2}', f'{courier["canceled_by_seller"]}', body_format)
            worksheet.write(f'H{first_string + 3}', f'Отменено заказчиком', body_format)
            worksheet.write(f'I{first_string + 3}', f'{courier["canceled_by_client"]}', body_format)
            worksheet.write(f'H{first_string + 4}', f'В процессе', body_format)
            worksheet.write(f'I{first_string + 4}', f'{courier["waitings"]}', body_format)
            first_string += 5
            num += 1


def body_delivery_clients_admin(worksheet, body_format, sellers, start_period, end_period):
    """Записываем продавцов"""
    if sellers:
        first_string = 4
        num = 1
        for seller in sellers:
            ls = first_string + 4

            worksheet.merge_range(f'B{first_string}:B{ls}', f'{num}', body_format)
            worksheet.merge_range(f'C{first_string}:C{ls}', f'{start_period}', body_format)
            worksheet.merge_range(f'D{first_string}:D{ls}', f'{end_period}', body_format)
            worksheet.merge_range(f'E{first_string}:E{ls}', f'{seller["location_name"]}', body_format)
            worksheet.merge_range(f'F{first_string}:F{ls}', f'{seller["delivery_order_seller_admin_id"]}', body_format)
            worksheet.merge_range(f'G{first_string}:G{ls}', f'{seller["admin_seller_telegram_id"]}', body_format)
            worksheet.merge_range(f'H{first_string}:H{ls}', f'{seller["admin_seller_name"]}', body_format)
            worksheet.write(f'I{first_string}', f'Всего', body_format)
            worksheet.write(f'J{first_string}', f'{seller["all_orders"]}', body_format)
            worksheet.write(f'I{first_string + 1}', f'Выполнено', body_format)
            worksheet.write(f'J{first_string + 1}', f'{seller["completed"]}', body_format)
            worksheet.write(f'I{first_string + 2}', f'Отменено поставщиком', body_format)
            worksheet.write(f'J{first_string + 2}', f'{seller["canceled_by_seller"]}', body_format)
            worksheet.write(f'I{first_string + 3}', f'Отменено заказчиком', body_format)
            worksheet.write(f'J{first_string + 3}', f'{seller["canceled_by_client"]}', body_format)
            worksheet.write(f'I{first_string + 4}', f'В процессе', body_format)
            worksheet.write(f'J{first_string + 4}', f'{seller["waitings"]}', body_format)

            first_string += 5
            num += 1


def write_admin_delivery_statistics(data):
    """Записываем статистику"""
    orders = get_delivery_orders(data['orders'], data['products'], data['numbers'])
    threads = []

    workbook = xlsxwriter.Workbook(data['path'])

    body_format = workbook.add_format(b_format)
    head_format = workbook.add_format(h_format)

    worksheet1 = workbook.add_worksheet('Показатели за период')
    worksheet2 = workbook.add_worksheet('Статистика заказов')
    worksheet3 = workbook.add_worksheet('Поставщики')
    worksheet4 = workbook.add_worksheet('Курьеры')
    worksheet5 = workbook.add_worksheet('Заказчики')

    o = threading.Thread(target=body_delivery_orders_admin, args=(worksheet2, body_format, orders,
                                                                  data['first_period'].strftime("%d.%m.%Y"),
                                                                  data['end_period'].strftime("%d.%m.%Y")))
    o.start()
    threads.append(o)

    u = threading.Thread(target=body_delivery_clients_admin,
                         args=(worksheet5, body_format, data['user_orders'], data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    u.start()
    threads.append(u)

    i = threading.Thread(target=body_delivery_indicators_admin, args=(worksheet1, body_format, data['indicators'],
                                                                      data['indicators_by_loc']))
    i.start()
    threads.append(i)

    s = threading.Thread(target=body_delivery_sellers_admin,
                         args=(
                             worksheet3, body_format, data["sellers_orders"], data['first_period'].strftime("%d.%m.%Y"),
                             data['end_period'].strftime("%d.%m.%Y")))
    s.start()
    threads.append(s)

    c = threading.Thread(target=body_delivery_couriers,
                         args=(worksheet4, body_format, data['couriers_orders'],
                               data['first_period'].strftime("%d.%m.%Y"),
                               data['end_period'].strftime("%d.%m.%Y")))
    c.start()
    threads.append(c)

    head_delivery_indicators_admin(worksheet1, head_format, body_format)
    head_delivery_orders_admin(worksheet2, head_format)
    head_delivery_sellers_admin(worksheet3, head_format)
    head_delivery_couriers(worksheet4, head_format)
    head_delivery_clients_admin(worksheet5, head_format)

    for x in threads:
        x.join()

    workbook.close()

    try:
        send_email(data['file_name'], data['file_name'], data['to_email'], data['path'], data['file_name'])

        os.remove(data['path'])
        return True
    except Exception as err:
        os.remove(data['path'])
        logging.error(err)
        return False
