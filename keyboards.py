from aiogram import types

import db


# Меню для админов
def admin_menu():
    menu = types.InlineKeyboardMarkup()
    welcome_message = types.InlineKeyboardButton(
        '💬Изменить приветственное сообщение', callback_data='change_welcomeMessage')
    mailing = types.InlineKeyboardButton('✉️Рассылка', callback_data='mailing')
    qiwi_token = types.InlineKeyboardButton(
        '🥝Изменить QIWI токен', callback_data='change_qiwi')
    crypto_token = types.InlineKeyboardButton(
        '🤖Изменить CryptoBot токен', callback_data='change_crypto')
    crystal = types.InlineKeyboardButton(
        '💎Изменить CrystalPAY', callback_data='change_crystal')
    price = types.InlineKeyboardButton(
        '💶Изменить цену', callback_data='change_price')
    menu.add(mailing)
    menu.add(welcome_message)
    menu.row(qiwi_token, crypto_token)
    menu.row(crystal)
    menu.add(price)
    return menu


# Отмена действия
def cancel():
    markup = types.InlineKeyboardMarkup()
    cancel_btn = types.InlineKeyboardButton('💢Отмена', callback_data='cancel')
    markup.add(cancel_btn)
    return markup


# Меню для пользователей
def user_menu():
    menu = types.InlineKeyboardMarkup(1)
    buy = types.InlineKeyboardButton('💸Купить', callback_data='buy')
    support = types.InlineKeyboardButton(
        '⚙️Поддержка', callback_data='support')
    menu.add(buy, support)
    return menu


# Кнопка назад
def back():
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(
        '↩️Назад', callback_data='back_start')
    markup.add(back_btn)
    return markup


# Методы оплаты
def payments():
    markup = types.InlineKeyboardMarkup(1)

    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    qiwi = types.InlineKeyboardButton('🥝QIWI', callback_data='qiwi')
    crypto = types.InlineKeyboardButton('🤖CryptoBot', callback_data='crypto')
    crystal = types.InlineKeyboardButton(
        '💎CrystalPAY', callback_data='crystal')

    if settings.qiwi_token is not None:
        markup.add(qiwi)

    if settings.crypto_token is not None:
        markup.add(crypto)

    if (settings.crystal_secret, settings.crystal_name) is not None:
        markup.add(crystal)

    back = types.InlineKeyboardButton('↩️Назад', callback_data='back_start')

    markup.add(back)
    return markup


# Ссылка и проверка оплаты QIWI
def qiwi(url: str, id: str | int):
    markup = types.InlineKeyboardMarkup(1)
    link = types.InlineKeyboardButton('📎Ссылка на оплату', url=url)
    check_pay = types.InlineKeyboardButton(
        '🔍Проверить оплату', callback_data=f'check|qiwi|{id}')
    back = types.InlineKeyboardButton('↩️Назад', callback_data='back_payments')
    markup.add(link, check_pay, back)
    return markup


# Ссылка и проверка оплаты Сrystal
def crystal(url: str, id: str | int):
    markup = types.InlineKeyboardMarkup(1)
    link = types.InlineKeyboardButton('📎Ссылка на оплату', url=url)
    check_pay = types.InlineKeyboardButton(
        '🔍Проверить оплату', callback_data=f'check|crystal|{id}')
    back = types.InlineKeyboardButton('↩️Назад', callback_data='back_payments')
    markup.add(link, check_pay, back)
    return markup


# Виды криптовалют Crypto
def types_crypto():
    markup = types.InlineKeyboardMarkup()
    btc = types.InlineKeyboardButton('1️⃣BTC', callback_data='type_btc')
    ton = types.InlineKeyboardButton('2️⃣TON', callback_data='type_ton')
    eth = types.InlineKeyboardButton('3️⃣ETH', callback_data='type_eth')
    usdt = types.InlineKeyboardButton('4️⃣USDT', callback_data='type_usdt')
    usdc = types.InlineKeyboardButton('5️⃣USDC', callback_data='type_usdc')
    busd = types.InlineKeyboardButton('6️⃣BUSD', callback_data='type_busd')
    back = types.InlineKeyboardButton('↩️Назад', callback_data='back_payments')
    markup.row(btc, ton, eth)
    markup.row(usdt, usdc, busd)
    markup.add(back)
    return markup


# Ссылка и проверка оплаты Crypto
def crypto(url: str, id: str | int):
    markup = types.InlineKeyboardMarkup(1)
    link = types.InlineKeyboardButton('📎Ссылка на оплату', url=url)
    check_pay = types.InlineKeyboardButton(
        '🔍Проверить оплату', callback_data=f'check|crypto|{id}')
    back = types.InlineKeyboardButton(
        '↩️Назад', callback_data='back_typeCrypto')
    markup.add(link, check_pay, back)
    return markup
