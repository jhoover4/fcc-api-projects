from datetime import datetime
import string
import random

from peewee import *

DATABASE = SqliteDatabase('sql.db')

class Urls(Model):
    def unique_string_generator(size=6):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))

    original_url = CharField()
    shortened_url = CharField(unique=True, default=unique_string_generator())
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE

class ImageSearches(Model):
    search_query = CharField()
    created_at = DateTimeField(default=datetime.now)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Urls, ImageSearches], safe=True)
    DATABASE.close()
