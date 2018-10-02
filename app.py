import json
import os
import re
from datetime import datetime

import requests
from flask import Flask, g, render_template, request, redirect, flash, jsonify
from werkzeug.utils import secure_filename

import config
import models
from resources.exercise import exercise_api
from resources.request_parser import request_parser_api
from resources.timestamp import timestamp_api

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = config.SECRET
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

app.register_blueprint(timestamp_api)
app.register_blueprint(request_parser_api)
app.register_blueprint(exercise_api)


@app.before_request
def before_request():
    """Connecting to peewee db."""

    g.db = models.DATABASE
    try:
        g.db.connect()
    except:
        pass


@app.after_request
def after_request(response):
    """Disconnecting from peewee db."""

    g.db.close()
    return response


@app.route('/')
def index():
    """List of all API endpoints available."""

    return render_template('index.html')


@app.route('/forms/timestamp')
def timestamp_index():
    """Use timestamp API with HTML form."""

    return render_template('timestamp.html')


# begin short_url routes and functions. Should probably move this to new file/folder at some point

def get_long_url(long_url):
    """Retrieve long url from database."""

    try:
        return models.Urls.get(models.Urls.original_url == long_url)
    except models.DoesNotExist:
        return None


def get_short_url(short_url):
    """Retrieve short url from database."""

    try:
        return models.Urls.get(models.Urls.shortened_url == short_url)
    except models.DoesNotExist:
        return None


def create_url(long_url):
    """Add long url to database."""

    new_url_entry = models.Urls(original_url=long_url)
    new_url_entry.save()

    return new_url_entry.shortened_url


def check_url(long_url):
    """Validate inputted long url."""

    result = re.match('^(https?:\/\/)?(www\.)?.*\..*', long_url)

    return result is not None


@app.route('/short-url')
def url_shortener_index():
    """Create short url with HTML form."""

    return render_template('url-shortener.html')


@app.route('/short-url/<long_url>')
def url_shortener(long_url):
    """Route for url shortener API."""

    if check_url(long_url) is False:
        return 'Please provide a valid url.'

    if get_long_url(long_url) is None:
        short_url = create_url(long_url)
    else:
        url_obj = get_long_url(long_url)
        short_url = url_obj._data['shortened_url']

    url_dict = {
        "original_url": long_url,
        "short_url": request.url_root + 'r/' + short_url
    }

    return json.dumps(url_dict)


@app.route('/r/<short_url>')
def redirect_short_url(short_url):
    """Use short url to redirect to long url in database."""

    url_obj = get_short_url(short_url)

    if url_obj is None:
        return "Your short url does not exist. Please <a 'href=/short-url/'>create one</a>."
    else:
        redirect_url = 'http://' + url_obj._data['original_url']

        return redirect(redirect_url, code=302)


# begin image search abstraction routes and functions. Should probably move this to new file/folder at some point

@app.route('/image-search')
def image_search_index():
    """Perform image search through HTML form."""

    return render_template('image-search.html')


def save_image_query(query):
    new_query_entry = models.ImageSearches(search_query=query)
    new_query_entry.save()


@app.route('/image-search/q/<image_query>')
def image_search(image_query):
    offset = 10
    save_image_query(image_query)

    r = requests.get('https://www.googleapis.com/customsearch/v1?q={0}'.format(image_query) +
                     '&num=10&cx=016705203389166446407:rqzbcag_hmc&alt=json&key=' +
                     'AIzaSyA6IdmbpfRWx_dWR0y_DugrbBvalu43yxQ' +
                     '&start={0}'.format(offset))

    data = json.loads(r.text)['items']

    return jsonify(data)


@app.route('/image-search/recent/')
def image_searches():
    """Returns images for image API."""

    final_list = []

    recent_searches = models.ImageSearches.select()
    # import pdb; pdb.set_trace()
    for search in recent_searches:
        final_list.append({'query': search.search_query,
                           'when': datetime.strftime(search.created_at, '%x %X')
                           })

    return jsonify(final_list)


# begin file metadata routes and functions. Should probably move this to new file/folder at some point

def allowed_file(filename):
    """Checks if file uploaded is allowed."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_FILE_EXTENSIONS


@app.route('/file-metadata', methods=['GET', 'POST'])
def upload_file():
    """Upload file route for file upload API."""

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file detected!')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = app.root_path + '\\uploads\\' + filename
            file.save(file_path)

            statinfo = os.stat(file_path)
            file_size = {'size': statinfo.st_size}

            os.remove(file_path)

            return jsonify(file_size)
    return render_template('file-metadata.html')


if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
