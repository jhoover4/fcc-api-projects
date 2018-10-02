from datetime import datetime

from peewee import *

DATABASE = SqliteDatabase('fcc_api.db')


class Url(Model):
    original_url = CharField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE


class ImageSearches(Model):
    search_query = CharField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE


class ExerciseUser(Model):
    username = CharField(unique=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE


class Exercise(Model):
    """Exercises that can be associated with each exercise user."""

    exercise_user = ForeignKeyField(ExerciseUser, backref='exercises')
    description = CharField()
    duration = IntegerField()
    date = DateField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Url, ImageSearches, ExerciseUser, Exercise], safe=True)
    DATABASE.close()
