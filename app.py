
import os
import re
from datetime import datetime
from hashlib import md5

from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)
from psycopg import sql
from werkzeug.utils import secure_filename

from db_utils import create_pool, query_append_check, run_query, select_query
from get_best_hosts import get_best_hosts
from get_best_listings import get_best_listing
from get_booking import get_bookings
from get_host import get_host
from get_listing import get_listing
from get_neighbourhoods import get_neighbourhoods
from get_reviews import get_reviews
from get_user import get_user
from post_booking import post_booking
from post_host import post_host
from post_user import post_user
from update_host import update_host
from update_user import update_user

# as per recommendation from @freylis, compile once only
CLEANR = re.compile('<.*?>')

ALL_ROWS_COUNT = 9223372036854775806


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


pool = create_pool()

app = Flask(__name__)
app.config.from_pyfile('env.py')
app.secret_key = b'eeabb196a8b469e1ca9f6c9f0133312cc2169632bd0491ab96d47e0ecd165f99'


######## LISTINGS ########
@app.route('/')
def get_listings():
    args_dic = {
        'count': int(request.args.get('count')) if request.args.get('count') else 12,
        'page': int(request.args.get('page')) if request.args.get('page') else 0,
        'neighbourhood': request.args.get('city') or None,
        'room_type': request.args.get('room_type') or None,
        'bedrooms': int(request.args.get('bedrooms')) if request.args.get('bedrooms') else None,
        'beds': int(request.args.get('beds')) if request.args.get('beds') else None,
        'rating': int(request.args.get('rating')) if (request.args.get('rating')) else None,
    }
    amenities = request.args.getlist('amenities') or None
    query_lst_args = {
        'min_price': request.args.get('min_price') or None,
        'max_price': request.args.get('max_price') or None,
        'is_superhost': True if request.args.get('is_superhost') == 'on' else None,
        'check_in': request.args.get('check_in') or None,
        'check_out': request.args.get('check_out') or None,
    }
    extra_query = []
    if (query_lst_args['is_superhost']):
        extra_query.append(
            sql.SQL("\nINNER JOIN hosts ON hosts.id = listings.host_id")
        )
        extra_query.append(
            sql.SQL("\nWHERE hosts.is_superhost = %(is_superhost)s")
        )
    if (query_lst_args['min_price']):
        query_append_check(extra_query)
        extra_query.append(
            sql.SQL("price >= %(min_price)s")
        )
    if (query_lst_args['max_price']):
        query_append_check(extra_query)
        extra_query.append(
            sql.SQL("price <= %(max_price)s")
        )
    if (query_lst_args['check_in'] or query_lst_args['check_out']):
        query_append_check(extra_query)
        if (query_lst_args['check_in'] and query_lst_args['check_out']):
            extra_query.append(
                sql.SQL("listings.id NOT IN (SELECT DISTINCT listing_id FROM booking WHERE start_date <= %(check_in)s AND end_date >= %(check_in)s OR start_date <= %(check_out)s AND end_date >= %(check_out)s AND listing_id = listings.id)")
            )
        elif query_lst_args['check_in']:
            extra_query.append(
                sql.SQL("listings.id NOT IN (SELECT DISTINCT listing_id FROM booking WHERE start_date <= %(check_in)s AND end_date >= %(check_in)s AND listing_id = listings.id)")
            )
        else:
            extra_query.append(
                sql.SQL("listings.id NOT IN (SELECT DISTINCT listing_id FROM booking WHERE start_date <= %(check_out)s AND end_date >= %(check_out)s AND listing_id = listings.id)")
            )
    if (amenities):
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
    neighbourhood_lst = [neighbourhood['neighbourhood']
                         for neighbourhood in neighbourhoods]
    listings_with_starts = []
    for listing in listings:
        listing['stars'] = "⭐"*int(listing['rating']
                                   ) if listing['rating'] else "No reviews"
        listings_with_starts.append(listing)
    message = {
        "authenticated": session.get("authenticated"),
        "user_id": session.get('user_id'),
        "host_id": session.get("host_id"),
        "listings": listings_with_starts,
        "cities": neighbourhood_lst,
        "selected_city": args_dic['neighbourhood']
    }
    return render_template('index.html', message=message)


@app.route('/listings/<id>', methods=['GET', 'POST'])
def listing_get_handler(id):
    query_lst = [
        sql.SQL('\nLEFT JOIN hosts ON hosts.id = listings.host_id'),
        sql.SQL('\nLEFT JOIN users ON users.id = hosts.user_id'),
    ]
    listing = get_listing(pool, {
        'id': id,
        'extra_fields': [
            sql.Identifier('hosts', 'location') +
            sql.SQL(' AS host_location'),
            sql.Identifier('hosts', 'neighbourhood') +
            sql.SQL(' AS host_neighbourhood'),
            sql.Identifier('hosts', 'is_superhost') +
            sql.SQL(' AS host_is_superhost'),
            sql.Identifier('users', 'name') + sql.SQL(' AS host_name'),
            sql.Identifier('users', 'picture_url') +
            sql.SQL(' AS host_picture_url'),
        ],
        'extra_query': {
            'query_lst': query_lst,
        }
    })
    if not listing:
        abort(404, 'Listing not found')

    host_user = {
        'name': listing['host_name'],
        'id': listing['host_id']
    }
    reviews = get_reviews(pool, {'listing_id': id, 'count': 10})
    message = {
        "authenticated": session.get("authenticated"),
        "user_id": session.get('user_id'),
        "host_id": session.get("host_id"),
        "listing": listing,
        "host_user": host_user,
        "reviews": reviews,
    }
    if request.method == "GET":
        return render_template('listingDetail.html', message=message)

    if request.method == "POST":
        ft = request.form.get("form_type")

        if ft == "book":
            checkin = datetime.strptime(
                request.form.get("checkin"), "%Y-%m-%d").date()
            checkout = datetime.strptime(
                request.form.get("checkout"), "%Y-%m-%d").date()

            if checkin >= checkout:
                message["error"] = "Check-in date must be before check-out date"
                return render_template('listingDetail.html', message=message)

            days = (checkout - checkin).days
            if days < listing.get('min_nights'):
                message["error"] = f"Minimum nights required is {listing.get('min_nights')} days"
                return render_template('listingDetail.html', message=message)

            if days > listing.get('max_nights'):
                message["error"] = f"Maximum nights allowed is {listing.get('max_nights')} days"
                return render_template('listingDetail.html', message=message)

            bookings = get_bookings(pool, {
                'listing_id': id,
                'count': ALL_ROWS_COUNT,
            })
            bookings = [] if not bookings else bookings

            for booking in bookings:
                if (checkin >= booking.get("start_date") and checkin <= booking.get("end_date")) or (checkout >= booking.get("start_date") and checkout <= booking.get("end_date")):
                    message[
                        "error"] = f"Booking overlaps with another booking starting on {booking.get('start_date')} and ending on {booking.get('end_date')}"
                    return render_template('listingDetail.html', message=message)

            args = {
                "listing_id": id,
                "num_guests": request.form.get("guests"),
                "start_date": checkin,
                "end_date": checkout,
                "cost": request.form.get("cost"),
                "booker_id": session.get("user_id")
            }
            post_booking(pool, args, app.logger)
            return redirect(f"/users/{session.get('user_id')}/profile")

        if ft == "review":
            pass

        if ft == "add":
            pass


######## USERS ########
@app.route('/users/<id>/profile', methods=['GET', "POST"])
def get_user_profile_handler(id):
    if str(session.get("user_id")) != id:
        return redirect("/")

    user = get_user(pool, {'id': id})

    bookings = get_bookings(pool, {
        'booker_id': id,
        'count': ALL_ROWS_COUNT,
        'extra_fields': [
            sql.Identifier('listings', 'name') +
            sql.SQL(' AS listing_name'),
        ],
        'extra_query': {
            'query_lst': [sql.SQL('\nLEFT JOIN listings ON listings.id = bookings.listing_id')],
        }
    })
    if user is None:
        abort(404, 'User not found')

    if request.method == "GET":
        message = {
            "authenticated": session.get("authenticated"),
            "user_id": session.get('user_id'),
            "host_id": session.get("host_id"),
            "user": user,
            "bookings": bookings
        }
        return render_template('user_profile.html', message=message)

    if request.method == "POST":
        new_picture_url = request.files.get("new_profile_picture")
        if not new_picture_url:
            new_picture_url = user.get("picture_url")
        else:
            fn = md5(secure_filename(
                new_picture_url.filename.split(".")[0]).strip().encode("utf-8")).hexdigest() + "." + new_picture_url.filename.split(".")[1]
            image_path = os.path.join(os.getcwd(), "static", "images", fn)
            new_picture_url.save(image_path)
            new_picture_url = url_for("static", filename="images/" + fn)

        new_name = request.form.get('new_name').strip()
        new_email = request.form.get('new_email').strip()
        if not new_name or not new_email:
            message = {
                "authenticated": session.get("authenticated"),
                "user_id": session.get('user_id'),
                "host_id": session.get("host_id"),
                "error": "Enter name or email to update!",
                "user": user,
                "bookings": bookings,
            }
            return render_template('user_profile.html', message=message)

        old_password = request.form.get(
            'old_password').strip()
        new_password = request.form.get(
            'new_password').strip()
        confirm_password = request.form.get(
            'confirm_password').strip()

        if old_password:
            old_password = md5(old_password.encode("utf-8")).hexdigest()
            if old_password != user.get("password"):
                message = {
                    "authenticated": session.get("authenticated"),
                    "user_id": session.get('user_id'),
                    "host_id": session.get("host_id"),
                    "error": "Old password is incorrect! Please try again.",
                    "user": user,
                    "bookings": bookings,
                }
                return render_template('user_profile.html', message=message)
            else:
                if new_password:
                    new_password = md5(
                        new_password.encode("utf-8")).hexdigest()
                    confirm_password = md5(
                        confirm_password.encode("utf-8")).hexdigest()
                    if confirm_password != new_password:
                        message = {
                            "authenticated": session.get("authenticated"),
                            "user_id": session.get('user_id'),
                            "host_id": session.get("host_id"),
                            "error": "New passwords don't match! Try again.",
                            "user": user,
                            "bookings": bookings,
                        }
                        return render_template('user_profile.html', message=message)
                    else:
                        args = {
                            "name": new_name,
                            "email": new_email,
                            "picture_url": new_picture_url,
                            "password": new_password
                        }
                        user_id = update_user(pool, args, id)
                        if user_id is None:
                            message = {
                                "authenticated": session.get("authenticated"),
                                "user_id": session.get('user_id'),
                                "host_id": session.get("host_id"),
                                "error": "Something went wrong! Please try again.",
                                "user": user,
                                "bookings": bookings,
                            }
                            return render_template('user_profile.html', message=message)

                        return redirect(f"/users/{user.get('id')}/profile")
                else:
                    message = {
                        "authenticated": session.get("authenticated"),
                        "user_id": session.get('user_id'),
                        "host_id": session.get("host_id"),
                        "error": "Enter new password to update!",
                        "user": user,
                        "bookings": bookings,
                    }
                    return render_template('user_profile.html', message=message)
        else:
            args = {
                "name": new_name,
                "email": new_email,
                "picture_url": new_picture_url,
                "password": user.get("password")
            }
            user_id = update_user(pool, args, id)
            if user_id is None:
                message = {
                    "authenticated": session.get("authenticated"),
                    "user_id": session.get('user_id'),
                    "host_id": session.get("host_id"),
                    "error": "Something went wrong! Please try again.",
                    "user": user,
                    "bookings": bookings,
                }
                return render_template('user_profile.html', message=message)

            return redirect(f"/users/{user.get('id')}/profile")


######## HOSTS ########
@app.route("/hosts/<id>/profile", methods=["GET", "POST"])
def host_profile(id):
    host = get_host(pool, {"id": id})
    if host == None:
        abort(404, 'Host not found')

    host_user = get_user(pool, {"id": host.get("user_id")})

    if request.method == "GET":
        message = {
            "authenticated": session.get("authenticated"),
            "user_id": session.get('user_id'),
            "host_id": session.get("host_id"),
            "host": host,
            "host_user": host_user
        }
        if str(session.get("host_id")) != id:
            template = "host_view_profile.html"
        else:
            template = "host_edit_profile.html"

        return render_template(template, message=message)

    if request.method == "POST":
        args = {
            "about": request.form.get("about"),
            "location": request.form.get("location"),
            "neighbourhood": request.form.get("neighbourhood")
        }
        host_id = update_host(pool, args, id)

        if not host_id:
            message = {
                "authenticated": session.get("authenticated"),
                "user_id": session.get('user_id'),
                "host_id": session.get("host_id"),
                "host": host,
                "host_user": host_user,
                "error": "Something went wrong. Please try again."
            }
            return render_template("host_edit_profile.html", message=message)

        return redirect(f"/hosts/{host_id}/profile")


######## AUTHENTICATION ########
@app.route('/signin', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'GET':
        if session.get('authenticated') is True:
            return redirect("/")

        message = {
            "authenticated": session.get("authenticated"),
            "user_id": session.get('user_id'),
            "host_id": session.get("host_id")
        }
        return render_template('signin.html', message=message)

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = md5(request.form.get(
            "password").strip().encode("utf-8")).hexdigest()

        # get user
        args = {"email": email, "password": password}
        fields = [
            sql.Identifier("users", "id"),
            sql.Identifier("users", "is_host")
        ]
        user = run_query(pool, lambda cur: select_query(
            cur, fields, 'users', args))

        if user.get("id"):
            session['authenticated'] = True
            session['user_id'] = user.get("id")
            if user.get("is_host"):
                session["host_id"] = run_query(
                    pool,
                    lambda cur: select_query(
                        cur,
                        [sql.Identifier("hosts", "id")],
                        'hosts',
                        {"user_id": user.get("id")}
                    )
                ).get("id")

            else:
                session["host_id"] = None

            return redirect("/")

        message = {
            "authenticated": session.get("authenticated"),
            "user_id": session.get('user_id'),
            "host_id": session.get("host_id"),
            "error": "Incorrect details!"
        }
        return render_template("signin.html", message=message)


@app.route("/signout", methods=["POST"])
def signout():
    session.pop("authenticated")
    session.pop("user_id")
    session.pop("host_id")
    return redirect("/")


@app.route('/signup', methods=['POST', "GET"])
def signup_handler():
    if request.method == 'GET':
        if session.get('authenticated') is True:
            return redirect("/")

        message = {
            "authenticated": session.get("authenticated"),
            "user_id": session.get('user_id'),
            "host_id": session.get("host_id")
        }
        return render_template('signup.html', message=message)

    if request.method == "POST":
        # check passwords
        password = md5(request.form.get(
            "password").strip().encode("utf-8")).hexdigest()
        confirm_password = md5(request.form.get(
            "confirm_password").strip().encode("utf-8")).hexdigest()
        if password != confirm_password:
            return render_template("signup.html", message={"error": "Passwords don't match. Try again."})

        # get remaining values
        email = request.form.get("email").strip()
        name = request.form.get("name").strip()

        is_host = request.form.get("is_host")
        if is_host is None:
            is_host = False
        else:
            is_host = True

        user_args = {
            "name": name,
            "email": email,
            "password": password,
            "is_host": is_host
        }
        user_id = post_user(pool, user_args, app.logger)

        if not user_id:
            message = {
                "authenticated": session.get("authenticated"),
                "user_id": session.get('user_id'),
                "host_id": session.get("host_id"),
                "error": "Email already exists, try another one."
            }
            return render_template("signup.html", message=message)

        host_id = None
        if is_host:
            host_args = {"user_id": user_id}
            host_id = post_host(pool, host_args, app.logger)

        session['authenticated'] = True
        session['user_id'] = user_id
        session['host_id'] = host_id

        if is_host:
            return redirect(f"/hosts/{host_id}/profile")

        return redirect("/")


######## ANALYTICS ########
@app.route('/best-listings', methods=['GET'])
def best_listings_handler():
    message = {
        "authenticated": session.get("authenticated"),
        "user_id": session.get('user_id'),
        "host_id": session.get("host_id"),
        "error": "Email already exists, try another one."
    }
    is_budget = request.args.get(
        'budget') if request.args.get('budget') else False
    args_dic = {
        'count': 10,
    }
    if (is_budget):
        args_dic['is_budget'] = True
    listings = get_best_listing(pool, args_dic)
    listings_with_stars = []
    for listing in listings:
        listing['stars'] = "⭐"*int(listing['rating']
                                   ) if listing['rating'] else "No reviews"
        listing['comments'] = cleanhtml(listing['comments'])
        listings_with_stars.append(listing)

    return render_template('best-listings.html', listings=listings_with_stars, message=message, is_budget=is_budget)


@app.route('/best-hosts', methods=['GET'])
def best_hosts_handler():
    message = {
        "authenticated": session.get("authenticated"),
        "user_id": session.get('user_id'),
        "host_id": session.get("host_id"),
        "error": "Email already exists, try another one."
    }
    args_dic = {
        'count': 10,
    }
    hosts = get_best_hosts(pool, args_dic)
    return render_template('best-hosts.html', hosts=hosts, message=message)
