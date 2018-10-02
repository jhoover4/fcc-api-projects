import datetime
import json
import unittest

from test_app import BaseTestCase

import models


class TestExerciseApi(BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.new_user = models.ExerciseUser.create(username='test_user')
        self.new_exercise = models.Exercise.create(
            exercise_user_id=1,
            description='This is a test.',
            duration=15,
            date=datetime.date(2017, 1, 1)
        )

    def test_get_users(self):
        """Test api/exercise/users get method."""

        response = self.app.get('/api/exercise/users')
        users = models.ExerciseUser.select()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)[0]['username'], users[0].username)

    def test_post_new_user(self):
        """Test api/exercise/new-user post method."""

        post_data = {
            'username': 'test_user2'
        }
        response = self.app.post('/api/exercise/new-user', data=post_data)

        self.assertEqual(response.status_code, 201)

        new_user = models.ExerciseUser.get(models.ExerciseUser.username == 'test_user2')
        new_user_dict = {
            '_id': new_user.id,
            'username': new_user.username
        }

        self.assertEqual(json.loads(response.data), new_user_dict)

    def test_post_existing_user(self):
        """Test api/exercise/new-user post method."""

        post_data = {
            'username': 'test_user'
        }
        response = self.app.post('/api/exercise/new-user', data=post_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {
            'message': 'User with that name already exists.'
        })

    def test_post_new_exercise(self):
        """Test api/exercise/add post method."""

        post_data = {
            'userId': 1,
            'description': 'This is a second test.',
            'duration': 60
        }
        response = self.app.post('/api/exercise/add', data=post_data)

        user_dict = {
            '_id': self.new_user.id,
            'username': self.new_user.username,
            'exercises': [
                {
                    'date': datetime.datetime.strftime(self.new_exercise.date, '%Y-%m-%d'),
                    'description': self.new_exercise.description,
                    'duration': self.new_exercise.duration
                },
                {
                    'date': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'),
                    'description': 'This is a second test.',
                    'duration': 60
                }
            ]
        }

        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data), user_dict)

    def test_get_user_detail_id(self):
        """Test api/exercise/log post method with id attribute only."""

        response = self.app.get('/api/exercise/log/1')

        user_dict = {
            '_id': self.new_user.id,
            'username': self.new_user.username,
            'exercises': [
                {
                    'description': self.new_exercise.description,
                    'duration': self.new_exercise.duration,
                    'date': datetime.datetime.strftime(self.new_exercise.date, '%Y-%m-%d')
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), user_dict)

    def test_get_user_detail_limit(self):
        """Test api/exercise/log post method with id attribute only."""

        models.Exercise.create(
            exercise_user_id=1,
            description='This is a second test.',
            duration=60,
            date='10/01/18'
        )
        data = {
            'limit': 1
        }

        response = self.app.get('/api/exercise/log/1', query_string=data)

        user_dict = {
            '_id': self.new_user.id,
            'username': self.new_user.username,
            'exercises': [
                {
                    'description': self.new_exercise.description,
                    'duration': self.new_exercise.duration,
                    'date': datetime.datetime.strftime(self.new_exercise.date, '%Y-%m-%d')
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), user_dict)

    def test_get_user_detail_from(self):
        """Test api/exercise/log post method with from, to attributes."""

        exercise = models.Exercise.create(
            exercise_user_id=1,
            description='This is a second test.',
            duration=60,
            date=datetime.date(2018, 1, 1)
        )
        data = {
            'from': '2017-12-01'
        }

        response = self.app.get('/api/exercise/log/1', query_string=data)

        user_dict = {
            '_id': self.new_user.id,
            'username': self.new_user.username,
            'exercises': [
                {
                    'description': exercise.description,
                    'duration': exercise.duration,
                    'date': datetime.datetime.strftime(exercise.date, '%Y-%m-%d')
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), user_dict)

    def test_get_user_detail_from_to(self):
        """Test api/exercise/log post method with from, to attributes."""

        exercise = models.Exercise.create(
            exercise_user_id=1,
            description='This is a second test.',
            duration=60,
            date=datetime.date(2018, 1, 1)
        )
        data = {
            'from': '2016-01-01',
            'to': '2019-01-01'
        }

        response = self.app.get('/api/exercise/log/1', query_string=data)

        user_dict = {
            '_id': self.new_user.id,
            'username': self.new_user.username,
            'exercises': [
                {
                    'description': self.new_exercise.description,
                    'duration': self.new_exercise.duration,
                    'date': datetime.datetime.strftime(self.new_exercise.date, '%Y-%m-%d')
                },
                {
                    'description': exercise.description,
                    'duration': exercise.duration,
                    'date': datetime.datetime.strftime(exercise.date, '%Y-%m-%d')
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), user_dict)
