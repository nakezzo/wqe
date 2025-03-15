from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext

import config
import db
import keyboards
import payments
from states import States

bot = Bot(config.BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())


# Команды для меню
async def set_default_commands(dp):
    await bot.set_my_commands([
        types.BotCommand('start', '🏠')],
        types.BotCommandScopeAllPrivateChats())
    for admin in config.admins:
        await bot.set_my_commands([
            types.BotCommand('start', '🏠'),
            types.BotCommand('admin', '💻Панель управления')],
            types.BotCommandScopeChat(chat_id=admin))


# Панель управления
@dp.message_handler(commands=['admin'], chat_type='private')
async def admin_menu(msg: types.Message):
    if msg.from_id in config.admins:
        users = len(db.User.select())

        await msg.answer(f'<b>👀 Пользователей в боте: {users}\n\n💎 Выбери действие:</b>', reply_markup=keyboards.admin_menu())


# Изменения для бота
@dp.callback_query_handler(text_startswith='change_')
async def change(call: types.CallbackQuery, state: FSMContext):
    what_change = call.data.split('_')[1]

    await state.update_data(change=what_change)

    match what_change:
        case 'welcomeMessage':
            await bot.edit_message_text('<b>📝 Напиши новое приветственное сообщение</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())
        case 'qiwi':
            await bot.edit_message_text('<b>🥝 Отправь новый QIWI-P2P токен</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())
        case 'crypto':
            await bot.edit_message_text('<b>🤖 Отправь новый CryptoBot токен</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())
        case 'crystal':
            await bot.edit_message_text('<b>💎 Отправь новый CrystalPAY secret и CrystalPAY name в виде: secret name</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())
        case 'price':
            await bot.edit_message_text('<b>💸 Напиши новую цену для Telegram Premium</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())

    await States.change.set()


# Изменение чего-либо в боте
@dp.message_handler(state=States.change, chat_type='private')
async def change_something(msg: types.Message, state: FSMContext):
    what_change = await state.get_data()
    what_change = what_change['change']

    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    message = msg.text

    match what_change:
        case 'welcomeMessage':
            settings.welcome_message = message
            settings.save()

            await msg.answer('<b>💬 Приветственное сообщение успешно обновилось</b>', reply_markup=keyboards.admin_menu())
        case 'qiwi':
            settings.qiwi_token = message
            settings.save()

            await msg.answer('<b>🥝 QIWI успешно обновился</b>', reply_markup=keyboards.admin_menu())
        case 'crypto':
            settings.crypto_token = message
            settings.save()

            await msg.answer('<b>🤖 СryptoBot успешно обновился</b>', reply_markup=keyboards.admin_menu())
        case 'crystal':
            message = message.split()
            settings.crystal_secret = message[0]
            settings.crystal_name = message[1]
            settings.save()

            await msg.answer('<b>💎 CrystalPAY успешно обновился</b>', reply_markup=keyboards.admin_menu())
        case 'price':
            try:
                message = int(message)
                settings.price = message
                settings.save()

                await msg.answer('<b>💰 Цена успешно обновилась</b>', reply_markup=keyboards.admin_menu())
            except:
                await msg.answer('<b>❗️ Пожалуйста, напиши число</b>', reply_markup=keyboards.cancel())
                return

    await state.finish()


# Рассылка
@dp.callback_query_handler(text='mailing')
async def mailing(call: types.CallbackQuery):
    await bot.edit_message_text('<b>📝 Отправь сообщение для рассылки</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.cancel())

    await States.mailing.set()


# Начало рассылки
@dp.message_handler(content_types=types.ContentTypes.ANY, state=States.mailing, chat_type='private')
async def send_mailing(msg: types.Message, state: FSMContext):
    sent = 0
    not_sent = 0

    await msg.answer('<b>✅ Рассылка успешно создана</b>', reply_markup=keyboards.admin_menu())

    if msg.content_type == 'photo':

        if msg.caption is not None:

            for user in db.User.select():
                try:
                    await bot.send_photo(user.user_id, msg.photo[-1].file_id, msg.caption)

                    sent += 1
                except:
                    not_sent += 1

                    continue

        else:

            for user in db.User.select():
                try:
                    await bot.send_photo(user.user_id, msg.photo[-1].file_id)

                    sent += 1
                except:
                    not_sent += 1

                    continue

    elif msg.content_type == 'document':

        if msg.caption is not None:

            for user in db.User.select():
                try:
                    await bot.send_document(user.user_id, msg.document.file_id, caption=msg.caption)

                    sent += 1
                except:
                    not_sent += 1

                    continue

        else:

            for user in db.User.select():
                try:
                    await bot.send_document(user.user_id, msg.document.file_id)

                    sent += 1
                except:
                    not_sent += 1

                    continue

    elif msg.content_type == 'text':

        for user in db.User.select():
            try:
                await bot.send_message(user.user_id, msg.text)

                sent += 1
            except:
                not_sent += 1

                continue

    elif msg.content_type == 'video':

        if msg.caption is not None:

            for user in db.User.select():
                try:
                    await bot.send_video(user.user_id, msg.video.file_id, caption=msg.caption)

                    sent += 1
                except:
                    not_sent += 1

                    continue

        else:

            for user in db.User.select():
                try:
                    await bot.send_video(user.user_id, msg.video.file_id)

                    sent += 1
                except:
                    not_sent += 1

                    continue

    elif msg.content_type == 'animation':

        if msg.caption is not None:

            for user in db.User.select():
                try:
                    await bot.send_animation(user.user_id, msg.animation.file_id, caption=msg.caption)

                    sent += 1
                except:
                    not_sent += 1

                    continue

        else:

            for user in db.User.select():
                try:
                    await bot.send_animation(user.user_id, msg.animation.file_id)

                    sent += 1
                except:
                    not_sent += 1

                    continue

    await msg.answer(f'<b>🛎 Статистика рассылки:\n\n🔔 - {sent}\n🔕 - {not_sent}</b>')

    await state.finish()


# Отмена действия
@dp.callback_query_handler(text='cancel', state=[States.change, States.mailing])
async def cancel_action(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text('<b>✅ Ты успешно отменил действие</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.admin_menu())

    await state.finish()


# Начальное сообщение
@dp.message_handler(commands=['start'], chat_type='private')
async def start_message(msg: types.Message):
    if not db.User.get_or_none(db.User.user_id == msg.from_id):

        db.User.create(user_id=msg.from_id)

    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    await msg.answer(f'<b>{settings.welcome_message}</b>', reply_markup=keyboards.user_menu())


# Поддержка
@dp.callback_query_handler(text='support')
async def support(call: types.CallbackQuery):
    support = config.support

    await bot.edit_message_text(f'<b>⚙️ Наша поддержка: {support}</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.back())


# Покупка премиума
@dp.callback_query_handler(text='buy')
async def buy(call: types.CallbackQuery):
    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    await bot.edit_message_text(f'<b>💰 Цена: {settings.price} ₽\n💸 Выбери способ оплаты:</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.payments())


# Оплата киви
@dp.callback_query_handler(text='qiwi')
async def qiwi_pay(call: types.CallbackQuery):
    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    bill = await payments.create_bill_qiwi(settings.price)

    await bot.edit_message_text('<b>🔥 Оплати счёт и проверь оплату</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.qiwi(bill[1], bill[0]))


# Оплата кристал
@dp.callback_query_handler(text='crystal')
async def crystal_pay(call: types.CallbackQuery):
    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    bill = await payments.create_bill_crystal(settings.price)

    await bot.edit_message_text('<b>🔥 Оплати счёт и проверь оплату</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.crystal(bill[1], bill[0]))


# Оплата крипто
@dp.callback_query_handler(text='crypto')
async def crypto_pay(call: types.CallbackQuery):
    await bot.edit_message_text('<b>🪙 Выбери в какой криптовалюте хочешь оплатить счёт:</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.types_crypto())


# Выбор криптовалюты для крипто
@dp.callback_query_handler(text_startswith='type_')
async def type_crypto(call: types.CallbackQuery):
    crypto = call.data.split('_')[1]
    settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

    bill = payments.CryptoBot().create_bill(crypto, settings.price)

    await bot.edit_message_text('<b>🔥 Оплати счёт и проверь оплату</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.crypto(bill[1], bill[0]))


# Проверка оплаты
@dp.callback_query_handler(text_startswith='check')
async def check_payment(call: types.CallbackQuery):
    payment_method = call.data.split('|')[1]
    id = call.data.split('|')[2]

    match payment_method:
        case 'qiwi':
            payed = await payments.check_bill_qiwi(id)

            match payed:
                case 'PAID':
                    await bot.edit_message_text('<b>🎉 Спасибо за покупку! В скором времени вам будет выдан ТГ Премиум</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())

                    for admin in config.admins:
                        await bot.send_message(admin, f'<b>👤 Пользователь @{call.from_user.username} купил подписку</b>')
                case 'EXPIRED':
                    await bot.edit_message_text('<b>🧐 Счёт был просрочен, создай новый</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())
                case _:
                    await call.answer('⛔️ Счёт не оплачен')
        case 'crystal':
            payed = await payments.check_pay_crystal(id)

            match payed:
                case 'PAID':
                    await bot.edit_message_text('<b>🎉 Спасибо за покупку! В скором времени вам будет выдан ТГ Премиум</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())

                    for admin in config.admins:
                        await bot.send_message(admin, f'<b>👤 Пользователь @{call.from_user.username} купил подписку</b>')
                case _:
                    await call.answer('⛔️ Счёт не оплачен')
        case 'crypto':
            payed = payments.CryptoBot().get_bill_status(id)

            match payed:
                case 'paid':
                    await bot.edit_message_text('<b>🎉 Спасибо за покупку! В скором времени вам будет выдан ТГ Премиум</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())

                    for admin in config.admins:
                        await bot.send_message(admin, f'<b>👤 Пользователь @{call.from_user.username} купил подписку</b>')
                case 'expired':
                    await bot.edit_message_text('<b>🧐 Счёт был просрочен, создай новый</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())
                case _:
                    await call.answer('⛔️ Счёт не оплачен')


# Назад куда-либо
@dp.callback_query_handler(text_startswith='back_')
async def back(call: types.CallbackQuery):
    where = call.data.split('_')[1]

    match where:
        case 'start':
            settings = db.Settings.get(db.Settings.id == 1)  # type: ignore

            await bot.edit_message_text(f'<b>{settings.welcome_message}</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.user_menu())
        case 'payments':
            await bot.edit_message_text('<b>💸 Выбери способ оплаты:</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.payments())
        case 'typeCrypto':
            await bot.edit_message_text('<b>🪙 Выбери в какой криптовалюте хочешь оплатить счёт:</b>', call.from_user.id, call.message.message_id, reply_markup=keyboards.types_crypto())


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=set_default_commands)
