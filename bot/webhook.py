import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram.types import BufferedInputFile
from aiohttp import web

from bot.database.ORM.ORDER import export_order_to_excel_by_user, orm_process_payment
from bot.parametrs import session_maker, bot


async def t_bank_webhook(request: web.Request):
    data = await request.json()

    # Получаем ID платежа и его статус из данных вебхука
    payment_id = data.get('RebillId')  # ID платежа
    payment_status = data.get('Status')  # Статус платежа
    # Получаем данные из вложенного объекта Data
    metadata = data.get('Data', {})
    order_id = metadata.get('order_id')
    user_id=metadata.get('CUSTOMER_KEY')
    try:

        if payment_status == "CONFIRMED":
            async with session_maker() as session:
                try:
                    input_file = await orm_process_payment(session, int(order_id), int(user_id))

                    await bot.send_document(
                        chat_id=int(user_id),
                        document=input_file,
                        caption=f"📦 Ваш заказ №{order_id} успешно оплачен!"
                    )
                except Exception as e:
                    logging.error(f"Ошибка при обработке оплаты заказа {order_id}: {e}")

        return web.Response(status=200, text='OK')

    except Exception as e:
        logging.error(f"Ошибка при обработке вебхука от YooKassa: {e}")
        return web.Response(status=500)
