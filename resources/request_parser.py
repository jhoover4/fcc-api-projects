from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api


class RequestParser(Resource):
    @staticmethod
    def empty_string_if_none(value):
        if not value:
            return ""
        else:
            return value

    def get(self):
        """Returns json of various header information based on request."""

        data = {
            "ipaddress" : RequestParser.empty_string_if_none(request.remote_addr),
            "language" : RequestParser.empty_string_if_none(request.accept_languages.best),
            "software" : RequestParser.empty_string_if_none(request.user_agent.string),
        }

        return jsonify(data)


request_parser_api = Blueprint('resources.request_parser', __name__)
api = Api(request_parser_api)

api.add_resource(
    RequestParser,
    '/api/whoami',
    endpoint='request_parser'
)
