from flask import Flask, request, abort
from flask import render_template
from db_utils import create_pool, query_append_check
from get_host import get_host
from get_listing import get_listing
from get_user import get_user
from post_host import post_host
from post_user import post_user
from psycopg import sql
from get_neighbourhoods import get_neighbourhoods
import sys

pool = create_pool()

app = Flask(__name__)
app.config.from_pyfile('env.py')

@app.route('/')
def get_listings():
    args_dic = {
        'count': int(request.args.get('count')) if request.args.get('count') else 12,
        'page': int(request.args.get('page')) if request.args.get('page') else 0,
        'neighborhood': request.args.get('city') or None,
        'room_type': request.args.get('room_type') or None,
        'bedrooms': int(request.args.get('bedrooms')) if request.args.get('bedrooms')  else None,
        'beds': int(request.args.get('beds')) if request.args.get('beds') else None,
        'review_rating': int(request.args.get('review_rating')) if(request.args.get('review_rating')) else None,
    }
    amenities = request.args.getlist('amenities') or None
    query_lst_args = {
        'min_price': request.args.get('min_price') or None,
        'max_price': request.args.get('max_price') or None,
        'is_super_host': True if request.args.get('is_super_host') == 'on' else None,
    }
    extra_query = []
    if(query_lst_args['is_super_host']):
        extra_query.append(
            sql.SQL("\nINNER JOIN host ON host.id = listing.host_id")
        )
        extra_query.append(
            sql.SQL("\nWHERE host.is_super_host = %(is_super_host)s")
        )
    if(query_lst_args['min_price']):
        query_append_check(extra_query)
        extra_query.append(
            sql.SQL("price >= %(min_price)s")
        )
    if(query_lst_args['max_price']):
        query_append_check(extra_query)
        extra_query.append(
            sql.SQL("price <= %(max_price)s")
        )
    if(amenities):
        for i in range(len(amenities)):
            amenity = amenities[i]
            query_append_check(extra_query)
            extra_query.append(
                sql.SQL("{} = ANY(amenities)")
                    .format(
                        sql.Placeholder('amenity' + str(i))
                    )
            )

            query_lst_args['amenity' + str(i)] = amenity

    args_dic['extra_query'] = {
        'query_lst': extra_query,
        'args_dic': query_lst_args
    }
    listings = get_listing(pool, args_dic)
    neighbourhoods = get_neighbourhoods(pool)
    neighbourhood_lst = [neighbourhood['neighborhood'] for neighbourhood in neighbourhoods]
    listings_with_starts = []
    for listing in listings:
        listing['stars'] = "⭐"*int(listing['review_rating']) if listing['review_rating'] else "No reviews"
        listings_with_starts.append(listing)
    return render_template(
        'index.html',
        listings=listings_with_starts,
        user_id=request.args.get('user_id'),
        cities=neighbourhood_lst,
        selected_city=args_dic['neighborhood'],
        )

@app.route('/users/<id>', methods=['GET'])
def get_user_handler(id):
    user = get_user(pool, {'id': id})
    if(user == None):
        abort(404, 'User not found')
    print('User: ' + str(user), file=sys.stdout)
    return render_template('base.html', user_name=str(user['name']))

@app.route('/login', methods=['POST'])
def login_handler():
    args_dic = request.json
    result = post_user(pool, args_dic, app.logger)
    if(result == None):
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
    if(result == None):
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
    print('Listing id: ' + id, file=sys.stdout)
    listing = get_listing(pool, {
        'id': id
    })
    return render_template('index.html', message='Query params: ' + str(listing['id']))
