import random
import string
from datetime import datetime

from peewee import *

DATABASE = SqliteDatabase('fcc_api.db')


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

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Urls, ImageSearches], safe=True)
    DATABASE.close()
