import json

import requests
from pyqiwip2p import AioQiwiP2P

import db


class CryptoBot:

    '''Действия с API CryptoBot'''

    def __init__(self):
        settings = db.Settings.get(db.Settings.id == 1)  # type: ignore
        self.url = 'https://pay.crypt.bot/api/'
        self.token = {'Crypto-Pay-API-Token': settings.crypto_token}

    # Создание счёта Crypto
    def create_bill(self, cryptocurrency: str, total: int) -> list:
        currency = requests.get(
            f'{self.url}getExchangeRates', headers=self.token)

        match cryptocurrency:
            case 'btc':
                amount = str(
                    total / float(currency.json()['result'][0]['rate']))
            case 'ton':
                amount = str(
                    total / float(currency.json()['result'][30]['rate']))
            case 'eth':
                amount = str(
                    total / float(currency.json()['result'][15]['rate']))
            case 'usdt':
                amount = str(
                    total / float(currency.json()['result'][90]['rate']))
            case 'usdc':
                amount = str(
                    total / float(currency.json()['result'][75]['rate']))
            case 'busd':
                amount = str(
                    total / float(currency.json()['result'][60]['rate']))

        result = list()
        params = {'asset': f'{cryptocurrency}',
                  'amount': amount}  # type: ignore
        response = requests.get(
            f'{self.url}createInvoice', params, headers=self.token)
        result.append(response.json()['result']['invoice_id'])
        result.append(response.json()['result']['pay_url'])
        return result

    # Проверка оплаты счёта Crypto
    def get_bill_status(self, id: str) -> str:
        params = {'invoice_ids': id}
        response = requests.get(
            f'{self.url}getInvoices', params, headers=self.token)
        return response.json()['result']['items'][0]['status']


# Создание счёта QIWI
async def create_bill_qiwi(total: int):
    p2p = db.Settings.get(db.Settings.id == 1)  # type: ignore

    async with AioQiwiP2P(auth_key=p2p.qiwi_token) as p2p:
        bill = await p2p.bill(amount=total, lifetime=60)
        result = list()
        result.append(bill.bill_id)
        result.append(bill.pay_url)
        return result


# Проверка оплаты счёта QIWI
async def check_bill_qiwi(bill_id: str | int):
    p2p = db.Settings.get(db.Settings.id == 1)  # type: ignore

    async with AioQiwiP2P(auth_key=p2p.qiwi_token) as p2p:
        if (await p2p.check(bill_id)).status == 'PAID':
            return 'PAID'
        elif (await p2p.check(bill_id)).status == 'EXPIRED':
            return 'EXPIRED'


# Создание счёта CrystalPAY
async def create_bill_crystal(total: str | int):
    crystal = db.Settings.get(db.Settings.id == 1)  # type: ignore

    api_crystal = requests.get(
        f'https://api.crystalpay.ru/v1/?s={crystal.crystal_secret}&n={crystal.crystal_name}&o=receipt-create&amount={total}')

    data = json.loads(api_crystal.text)
    url = data.get('url')
    id_pay = data.get('id')

    result = list()

    result.append(id_pay)
    result.append(url)
    result.append(total)

    return result


# Проверка оплаты счёта CrystalPAY
async def check_pay_crystal(bill_id: str | int):
    crystal = db.Settings.get(db.Settings.id == 1)  # type: ignore

    api_crystal = requests.get(
        f'https://api.crystalpay.ru/v1/?s={crystal.crystal_secret}&n={crystal.crystal_name}&o=receipt-check&i={bill_id}')

    data = json.loads(api_crystal.text)
    status_payed = data.get('state')

    if status_payed == 'payed':
        return 'PAID'
