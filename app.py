from flask import Flask
from flask import render_template
from datetime import datetime

app = Flask(__name__)

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

	return render_template('timestamp.html', timestamp_data=data)

@app.route('/request-parse')
def request_header_api():
	return render_template('request-parse.html')

if __name__ == '__main__':
    app.run(debug=True)
