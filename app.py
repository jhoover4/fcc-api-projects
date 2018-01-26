import json, re, os
from datetime import datetime

from flask import Flask, g, render_template, request, redirect, flash
from werkzeug.utils import secure_filename

import models

DEBUG = True
ALLOWED_FILE_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = '/uploads'
SECRET = 'ASDF!@#$5%$@#$%fasdf'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = SECRET
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def before_request():
	"""Connecting to peewee db"""
	g.db = models.DATABASE
	g.db.connect()

@app.after_request
def after_request(response):
	"""Disconnecting from peewee db"""
	g.db.close()
	return response

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/timestamp/<timestamp>')
def time_api(timestamp):

	data = {'timestamp_received': timestamp, 'unix':'', 'natural':''}

	if timestamp.isdigit():
		try:
			date_obj = datetime.fromtimestamp(int(timestamp))
			data['natural'] = datetime.strftime(date_obj, '%B %d, %Y')
			data['unix'] = datetime.timestamp(date_obj)

		except ValueError:
			data['unix'] = None
			data['natural'] = None

		except OSError:
			data['unix'] = None
			data['natural'] = None
	else:
		try:
			date_obj = datetime.strptime(timestamp, '%B %d, %Y')
			data['natural'] = datetime.strftime(date_obj, '%B %d, %Y')
			data['unix'] = datetime.timestamp(date_obj)

		except ValueError:
			data['unix'] = None
			data['natural'] = None

	return render_template('timestamp.html', timestamp_data=json.dumps(data))

@app.route('/request-parse')
def request_header_api():
	return render_template('request-parse.html')


# begin short_url routes and functions. Should probably move this to new file/folder at some point

def get_long_url(long_url):
	try:
		return models.Urls.get(models.Urls.original_url == long_url)
	except models.DoesNotExist:
		return None

def get_short_url(short_url):
	try:
		return models.Urls.get(models.Urls.shortened_url == short_url)
	except models.DoesNotExist:
		return None

def create_url(long_url):
	new_url_entry = models.Urls(original_url=long_url)
	new_url_entry.save()

	return new_url_entry.shortened_url

def check_url(long_url):
	result = re.match('^(https?:\/\/)?(www\.)?.*\..*', long_url)

	return result != None

@app.route('/short-url/<long_url>')
def url_shortener(long_url):
	short_url = ''

	if check_url(long_url) == False:
		return 'Please provide a valid url.'

	if get_long_url(long_url) == None:
		short_url = create_url(long_url)
	else:
		url_obj = get_long_url(long_url)
		short_url = url_obj._data['shortened_url']

	url_dict = {
		 "original_url": long_url,
		 "short_url": request.url_root + 'r/' + short_url
	}

	return render_template('url-shortener.html', url_data=json.dumps(url_dict))

@app.route('/r/<short_url>')
def redirect_short_url(short_url):
	url_obj = get_short_url(short_url)

	if url_obj == None:
		return "Your short url does not exist. Please <a 'href=/short-url/'>create one</a>."
	else:
		redirect_url = 'http://' + url_obj._data['original_url']

		return redirect(redirect_url, code=302)

# begin file metadata routes and functions. Should probably move this to new file/folder at some point

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS

@app.route('/file-metadata/', methods=['GET', 'POST'])
def upload_file():
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
			file_size = {'size': statinfo.st_size }

			os.remove(file_path)

			return json.dumps(file_size)
	return render_template('file-metadata.html')

if __name__ == '__main__':
	models.initialize()
	app.run(debug=DEBUG)