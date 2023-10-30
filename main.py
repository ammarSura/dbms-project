from flask import Flask, abort, render_template, request

from db_utils import create_pool
from get_host import get_host
from get_listing import get_listing
from get_user import get_user
from post_host import post_host
from post_user import post_user

pool = create_pool()

app = Flask(__name__)
app.config.from_pyfile('env.py')


@app.route('/')
def get_root():
    message = "Airbnb"
    return render_template('index.html', message=message)


@app.route('/users/<id>', methods=['GET'])
def get_user_handler(id):
    user = get_user(pool, {'id': id})
    if (user == None):
        abort(404, 'User not found')
    return render_template('index.html', message='Query params: ' + str(user['name']))


@app.route('/login', methods=['POST'])
def login_handler():
    args_dic = request.json
    result = post_user(pool, args_dic, app.logger)
    if (result == None):
        abort(400, 'Missing param')
    else:
        return render_template('index.html', message=result)


@app.route('/host/<id>', methods=['GET'])
def host_get_handler(id):
    host = get_host(pool, {
        'id': id
    })
    return render_template('index.html', message='Query params: ' + str(host['id']))


@app.route('/host', methods=['POST'])
def host_post_handler():
    args_dic = request.json
    result = post_host(pool, args_dic, app.logger)
    if (result == None):
        abort(400, 'Missing param')
    else:
        return render_template('index.html', message=result)


@app.route('/listing', methods=['GET'])
def listings_get_handler():
    args_dic = {
        'count': request.args.get('count') or 10
    }
    listings = get_listing(pool, args_dic)
    return render_template('index.html', message='Query params: ' + str(len(listings)))


@app.route('/listing/<id>', methods=['GET'])
def listing_get_handler(id):
    listing = get_listing(pool, {
        'id': id
    })
    return render_template('index.html', message='Query params: ' + str(listing['id']))
