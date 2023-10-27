from flask import Flask, request, abort
from flask import render_template
from db_utils import run_query, create_pool
from user_methods import get_user, post_user
import sys

pool = create_pool()

app = Flask(__name__)
app.config.from_pyfile('env.py')

@app.route('/')
def get_root():
    message = "Airbnb"
    return render_template('index.html', message=message)

@app.route('/users/<id>', methods=['GET'])
def get_user_handler(id):
    user = run_query(pool, lambda cur: get_user(cur, { 'id': id }))
    return render_template('index.html', message='Query params: ' + str(user['id']))
@app.route('/login', methods=['POST'])
def login_handler():
    args_dic = request.json
    result = run_query(pool, lambda cur: post_user(cur, args_dic))
    if(result == None):
        abort(400, 'Missing param')
    else:
        return render_template('index.html', message=result)

@app.route('/host', methods=['GET'])
def post_handler():
    app.logger.info('Received this request method: %s', request.method)
    app.logger.info('Received this request body: %s', request.get_json().get('name'))
    return render_template('index.html', message='POST request')
