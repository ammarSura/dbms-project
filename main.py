from flask import Flask, request
from flask import render_template
from psycopg import Cursor
from logging_config import logging_config
import logging
from psycopg_pool import ConnectionPool
from db_utils import run_query, create_pool

pool = create_pool()

app = Flask(__name__)
app.config.from_pyfile('env.py')

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
