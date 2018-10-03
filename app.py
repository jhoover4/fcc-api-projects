import os

from flask import Flask, g, render_template, request, redirect, flash, jsonify, abort
from werkzeug.utils import secure_filename

import config
import models
from resources.exercise import exercise_api
from resources.image_search import image_search_api
from resources.request_parser import request_parser_api
from resources.timestamp import timestamp_api
from resources.url_shortener import url_shortener_api

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = config.SECRET
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

app.register_blueprint(timestamp_api)
app.register_blueprint(request_parser_api)
app.register_blueprint(exercise_api)
app.register_blueprint(url_shortener_api)
app.register_blueprint(image_search_api)


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


@app.route('/timestamp')
def timestamp_index():
    """Html page explaining timestamp API."""

    return render_template('timestamp.html')


@app.route('/request-parser')
def request_parser_index():
    """Html page explaining request parser API."""

    return render_template('request_parser.html')


@app.route('/shorturl')
def url_shortener_index():
    """Html page explaining url shortener API."""

    return render_template('url_shortener.html')


@app.route('/api/shorturl/<url_id>')
def url_shortener_redirect(url_id):
    """Route for url shortener API."""

    try:
        url = models.Url.get(models.Url.id == url_id)
    except models.DoesNotExist:
        abort(404)
    else:
        return redirect(url.original_url)


@app.route('/exercise')
def exercise_tracker_index():
    """Html page explaining exercise tracker API."""

    return render_template('exercise_tracker.html')


@app.route('/image-search')
def image_search_index():
    """Perform image search through HTML form."""

    return render_template('image_search.html')


def allowed_file(filename):
    """Checks if file uploaded is allowed."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_FILE_EXTENSIONS


@app.route('/file-metadata', methods=['GET', 'POST'])
def upload_file():
    """Upload file route for file upload API."""

    if request.method == 'POST':
        # check if the post request has the file part
        if 'upfile' not in request.files:
            flash('No file detected!')
            return redirect(request.url)
        file = request.files['upfile']

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
    return render_template('file_metadata.html')


if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
