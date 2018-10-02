import datetime

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal, url_for, marshal_with, abort

import models

user_fields = {
    '_id': fields.Integer(attribute='id'),
    'username': fields.String
}

exercise_fields = {
    'description': fields.String,
    'duration': fields.Integer,
    'date': fields.String
}

user_fields_with_exercises = {
    '_id': fields.Integer(attribute='id'),
    'username': fields.String,
    'exercises': fields.Nested(exercise_fields)
}


def date_parser(date_arg):
    """Value must be valid date in yyyy-mm-dd format."""

    return datetime.datetime.strptime(date_arg, '%Y-%m-%d')


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No name provided.',
            location=['form', 'json']
        )

        super().__init__()

    def get(self):
        """Returns a list of all exercise users."""

        users = [marshal(user, user_fields) for user in models.ExerciseUser.select()]

        return users

    @marshal_with(user_fields)
    def post(self):
        """Creates a new user."""

        args = self.reqparse.parse_args()

        try:
            user = models.ExerciseUser.create(username=args['username'])
        except models.IntegrityError:
            abort(400, message='User with that name already exists.')
        else:
            return user, 201, {'Location': url_for('resources.exercise.user', userId=user.id)}


class UserDetail(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'from',
            type=date_parser,
            help='Date must be in yyyy-mm-dd format.',
            location=['form', 'args']
        )
        self.reqparse.add_argument(
            'to',
            type=date_parser,
            help='Date must be in yyyy-mm-dd format.',
            location=['form', 'args']
        )
        self.reqparse.add_argument(
            'limit',
            type=int,
            location=['form', 'args']
        )

        super().__init__()

    def get(self, userId):
        """Returns user information with all exercises optionally filtered."""

        args = self.reqparse.parse_args()

        exercises = models.Exercise.select().where(
            models.Exercise.exercise_user_id == userId
        ).order_by(models.Exercise.id)

        if args.get('from'):
            exercises = exercises.select().where(
                models.Exercise.date >= args.get('from')
            ).order_by(models.Exercise.id)

        if args.get('to'):
            exercises = exercises.select().where(
                models.Exercise.date >= args.get('from')
            ).order_by(models.Exercise.id)

        if args.get('limit'):
            exercises = exercises[:args.get('limit')]

        user = marshal(models.ExerciseUser.get(id=userId), user_fields_with_exercises)
        user['exercises'] = [marshal(exercise, exercise_fields) for exercise in exercises]

        return user


class ExerciseLog(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'userId',
            required=True,
            help='userId is required.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'description',
            required=True,
            help='description is required.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'duration',
            required=True,
            help='duration is required.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'date',
            type=date_parser,
            help='Date must be in yyyy-mm-dd format.',
            location=['form', 'json']
        )

        super().__init__()

    def post(self):
        """Creates a new exercise for user."""

        args = self.reqparse.parse_args()

        if not args['date']:
            args['date'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        models.Exercise.create(exercise_user=args['userId'], **args)

        user = models.ExerciseUser.get(id=args['userId'])

        marshalled_user = marshal(models.ExerciseUser.get(id=args['userId']), user_fields_with_exercises)
        marshalled_user['exercises'] = [marshal(exercise, exercise_fields) for exercise in user.exercises]

        return marshalled_user, 201, {'Location': url_for('resources.exercise.user', userId=args['userId'])}


exercise_api = Blueprint('resources.exercise', __name__)
api = Api(exercise_api)

api.add_resource(
    UserList,
    '/api/exercise/users',
    '/api/exercise/new-user',
    endpoint='users'
)
api.add_resource(
    UserDetail,
    '/api/exercise/log/<userId>',
    endpoint='user'
)
api.add_resource(
    ExerciseLog,
    '/api/exercise/add',
    endpoint='exercise'
)
