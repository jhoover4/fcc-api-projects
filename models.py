from datetime import datetime

from peewee import *

DATABASE = SqliteDatabase('sql.db')

class Urls(Model):
    original_url = Charfield()
    shortened_url = Charfield(unique=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE
