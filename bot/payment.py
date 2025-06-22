import hashlib
from datetime import datetime

import aiohttp

from bot.database.models import Order
from bot.parametrs import terminal_password, terminal_key


def generate_token_tBank(r):
    t = []

    for key, value in r.items():
        t.append({key: value})
    t = sorted(t, key=lambda x: list(x.keys())[0])
    t = "".join(str(value) for item in t for value in item.values())
    sha256 = hashlib.sha256()
    sha256.update(t.encode('utf-8'))
    t = sha256.hexdigest()
    r["Token"] = t
    return r

async def send_post_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            print(f"Status: {response.status}")
            if response.status == 200:
                response_data = await response.json()
                return response_data
            else:
                print('Вернуть обратно')

async def create_payment_from_order(
    order: Order,
    user_id: int,
) -> str:
    from datetime import datetime

    current_time = datetime.now()
    unique_time = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]

    items = []
    total_amount = 0  # копейки

    for item in order.items:
        price = int(float(item.product.price) * 100)  # в копейках
        quantity = item.quantity
        amount = price * quantity
        total_amount += amount

        items.append({
            "Name": item.product.name[:64],
            "Price": price,
            "Quantity": quantity,
            "Amount": amount,
            "Tax": "none",
        })

    payment_json = {
        "TerminalKey": terminal_key,
        "Amount": total_amount,
        "OrderId": unique_time,
        "Password": terminal_password,
        "Description": f"Оплата заказа №{order.id}",
        "CustomerKey": str(user_id),
        "Recurrent": "N",
    }

    payment_json = generate_token_tBank(payment_json)

    payment_json.update({
        "DATA": {
            'order_id': order.id,
            'OperationInitiatorType': "1",
        },
        "Receipt": {
            "Email": "lipponka@mail.ru",
            "Inn": "645116875010",
            "FullName": "Рожкова Наталия Андреевна",
            "Phone": "+79297725100",
            "Taxation": "usn_income",
            "Items": items
        }
    })

    res = await send_post_request('https://securepay.tinkoff.ru/v2/Init', payment_json)
    print(res)
    return res['PaymentURL']


