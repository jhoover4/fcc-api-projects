import re

import requests
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal_with

import models

url_fields = {
    'original_url': fields.String,
    'short_url': fields.Integer(attribute='id')
}


def valid_url(url):
    """Checks that incoming url is properly formatting and hits a live site."""

    format_result = re.match('^(https?:\/\/)?(www\.)?.*\..*', url)

    if format_result is not None:
        if 'http' not in url:
            url = 'https://' + url

        try:
            request = requests.get(url)
        except requests.ConnectionError:
            raise ValueError(f"Invalid URL.")
        else:
            if request.status_code == 200:
                return url
            else:
                ValueError(f"{url} returned {request.status_code}")

    raise ValueError("Invalid URL format.")


class UrlShortenerCreation(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'url',
            required=True,
            help='Invalid URL.',
            location=['form', 'json'],
            type=valid_url
        )

        super().__init__()

    @marshal_with(url_fields)
    def post(self):
        """Creates a new url and returns id to use."""

        args = self.reqparse.parse_args()
        original_url = args.get('url')

        try:
            url_data = models.Url.get(models.Url.original_url == original_url)
            return url_data, 200
        except models.DoesNotExist:
            url_data = models.Url.create(original_url=original_url)
            return url_data, 201


url_shortener_api = Blueprint('resources.url_shortener', __name__)
api = Api(url_shortener_api)

api.add_resource(
    UrlShortenerCreation,
    '/api/shorturl/new',
    endpoint='url_shortener_new'
)
