from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

from flask import Flask, request
from flask import render_template
import sys

app = Flask(__name__)

@app.route('/')
def hello_world():
    message = "Hello, World"
    return render_template('index.html', message=message)

@app.route('/crud/<name>/<name2>', methods=['GET'])
def get_handler(name, name2):
    argsDic = request.args.to_dict()
    argsList = list(argsDic.values())
    app.logger.info('Received this request method: %s', request.method)
    app.logger.info('Received these query params: %s', argsList)
    app.logger.info('Received these path params: %s, %s', name, name2)
    return render_template('index.html', message='Query params: ' + ' '.join(map(str, argsList)))

@app.route('/crud', methods=['POST'])
def post_handler():
    app.logger.info('Received this request method: %s', request.method)
    app.logger.info('Received this request body: %s', request.get_json().get('name'))
    return render_template('index.html', message='POST request')
