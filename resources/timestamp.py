import datetime
import json

import pytz
from flask import Blueprint, jsonify
from flask_restful import Resource, Api, reqparse


class BaseTimestamp(Resource):
    @staticmethod
    def create_time_data(date):
        """
        Formats timestamp into needed data format.
        Data will contain both a unix and utc version of timestamp provided.
        """

        gmt = pytz.timezone('GMT')
        local_date = gmt.localize(date)

        return {
            'unix': datetime.datetime.timestamp(date),
            'utc': datetime.datetime.strftime(local_date, '%a, %d %b %Y %B %X %Z')
        }


class CurrentTimestamp(BaseTimestamp):
    def get(self):
        """If no timestamp is provided use current time."""

        date = datetime.datetime.now()

        data = self.create_time_data(date)
        return jsonify(data)


class ConvertTimestamp(BaseTimestamp):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'timestamp',
            required=True,
            help='No timestamp provided.',
            location=['form', 'json']
        )

        super().__init__()

    def get(self, timestamp):
        """
        Returns two versions of timestamp based on what user provided in URI.
        Timestamp provided can either be YY-MM-DD or a unix timestamp.
        See this link for more details: https://curse-arrow.glitch.me.
        """

        if timestamp.isdigit():
            date = datetime.datetime.fromtimestamp(int(timestamp))
        else:
            try:
                date = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

            except ValueError:
                try:
                    date = datetime.datetime.fromtimestamp(float(timestamp))

                except ValueError:
                    return json.dumps({'error': 'Invalid Date'}), 400

        data = self.create_time_data(date)
        return jsonify(data)


timestamp_api = Blueprint('resources.timestamp', __name__)
api = Api(timestamp_api)

api.add_resource(
    CurrentTimestamp,
    '/api/timestamp',
    endpoint='timestamp'
)

api.add_resource(
    ConvertTimestamp,
    '/api/timestamp/<timestamp>',
    endpoint='timestamps'
)
