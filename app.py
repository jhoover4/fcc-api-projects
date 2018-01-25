import json
from datetime import datetime

from flask import Flask, g, render_template, request

import models

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

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

def get_url(long_url):
	try:
		a = models.Urls.get(models.Urls.original_url == long_url)
		return a
	except models.DoesNotExist:
		return None

def create_url(long_url):
	new_url_entry = models.Urls(original_url=long_url)
	new_url_entry.save()

	return new_url_entry.shortened_url

@app.route('/short-url/<long_url>')
def url_shortener(long_url):
	short_url = ''

	if get_url(long_url) == None:
		short_url = create_url(long_url)
	else:
		data_obj = get_url(long_url)
		short_url = data_obj._data['shortened_url']

	url_dict = {
		 "original_url": long_url,
		 "short_url": request.url_root + 'r/' + short_url
	}

	return render_template('url-shortener.html', url_data=json.dumps(url_dict))

@app.route('/short-url/r/<long_url>')
def redirect_url():
	pass

if __name__ == '__main__':
	models.initialize()
	app.run(debug=DEBUG)
