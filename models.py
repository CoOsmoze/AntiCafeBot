from itertools import count
from peewee import *

db = SqliteDatabase('database.sqlite')

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(primary_key=True)
    status = CharField()
    name = CharField()
    username = CharField()

class Room(BaseModel):
    id = AutoField()
    name = CharField()
    price = IntegerField()
    max_people_count = IntegerField()

class Order(BaseModel):
    id = AutoField()
    status = CharField(default = "В обработке")
    user = ForeignKeyField(User, backref='order', on_delete='CASCADE')
    room = CharField()
    count_people = IntegerField()
    phone = CharField()



db.create_tables([User, Room, Order])