from peewee import IntegerField, Model, SqliteDatabase, TextField

db = SqliteDatabase('DataBase.db')


# Настройки для бота
class Settings(Model):
    welcome_message = TextField()
    qiwi_token = TextField(null=True)
    crypto_token = TextField(null=True)
    crystal_secret = TextField(null=True)
    crystal_name = TextField(null=True)
    price = IntegerField()

    class Meta:
        database = db


# ID пользователей бота
class User(Model):
    user_id = IntegerField()

    class Meta:
        database = db
