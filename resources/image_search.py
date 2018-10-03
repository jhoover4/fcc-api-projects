import json

import requests
from flask import Blueprint, jsonify
from flask_restful import Resource, Api, reqparse, fields, marshal, abort

import config
import models

DEFAULT_OFFSET = 10
DEFAULT_RETURNED = 10
GOOGLE_KEY = config.GOOGLE_API_KEY

recent_search_fields = {
    'query': fields.String(attribute='search_query'),
    'when': fields.DateTime(attribute='created_at'),
}


class ImageSearch(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'offset',
            type=int,
            location=['form', 'args']
        )
        self.reqparse.add_argument(
            'query',
            type=str,
            location=['form', 'args']
        )

        super().__init__()

    def get(self, query=None):
        """Returns json of various header information based on request."""

        args = self.reqparse.parse_args()

        if not query:
            query = args.get('query')

            if not query:
                abort(400, message='Query is required.')

        if args.get('offset'):
            offset = args.get('offset')
        else:
            offset = DEFAULT_OFFSET

        new_query_entry = models.ImageSearch(search_query=query)
        new_query_entry.save()

        google_img_query = f"https://www.googleapis.com/customsearch/v1?q={query}&num={DEFAULT_RETURNED}" \
                           f"&cx=016705203389166446407:rqzbcag_hmc&alt=json&key={GOOGLE_KEY}&start={offset}"

        try:
            r = requests.get(google_img_query)
        except:
            abort(400, message='Query was not successful. Please try again.')
            return

        data = json.loads(r.text)['items']

        return jsonify(data)


class SearchHistory(Resource):
    def get(self):
        """Returns json of various header information based on request."""

        recent_searches = [marshal(search, recent_search_fields) for search in models.ImageSearch.select()]

        return recent_searches


image_search_api = Blueprint('resources.image_search', __name__)
api = Api(image_search_api)

api.add_resource(
    ImageSearch,
    '/api/image-search/<query>',
    '/api/image-search',
    endpoint='image_search'
)
api.add_resource(
    SearchHistory,
    '/api/image-search/recent',
    endpoint='search_history'
)
