from hashlib import md5

from flask import Flask, abort, redirect, render_template, request

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
    return render_template('index.html', message="Airbnb")


@app.route('/users/<id>', methods=['GET'])
def get_user_handler(id):
    user = get_user(pool, {'id': id})
    if (user == None):
        abort(404, 'User not found')
    return render_template('index.html', message=user)


@app.route('/users/<id>/profile', methods=['GET', "POST"])
def get_user_profile_handler(id):
    user = get_user(pool, {'id': id})
    bookings = []  # get bookings
    if (user == None):
        abort(404, 'User not found')
    print(user)

    if request.method == "GET":
        message = {"user": user, "bookings": bookings}
        return render_template('user_profile.html', message=message)

    if request.method == "POST":
        new_name = request.form.get('new_name').strip()
        new_email = request.form.get('new_email').strip()
        if not new_name or not new_email:
            message = {
                "error": "Enter name or email to update!",
                "user": user,
                "bookings": bookings,
            }
            return render_template('user_profile.html', message=message)

        old_password = md5(request.form.get(
            'old_password').strip().encode("utf-8")).hexdigest()
        new_password = md5(request.form.get(
            'new_password').strip().encode("utf-8")).hexdigest()
        confirm_password = md5(request.form.get(
            'confirm_password').strip().encode("utf-8")).hexdigest()

        if old_password:
            if old_password != user.password:
                message = {
                    "error": "Old password is incorrect! Please try again.",
                    "user": user,
                    "bookings": bookings,
                }
                return render_template('user_profile.html', message=message)
            else:
                if new_password:
                    if confirm_password != new_password:
                        message = {
                            "error": "New passwords don't match! Try again.",
                            "user": user,
                            "bookings": bookings,
                        }
                        return render_template('user_profile.html', message=message)
                    else:
                        # update user using new_password, new_name, new_email
                        return redirect(f"/users/{user.id}/profile")
                else:
                    message = {
                        "error": "Enter new password to update!",
                        "user": user,
                        "bookings": bookings,
                    }
                    return render_template('user_profile.html', message=message)
        else:
            # update user call using user.password, new_name, new_email
            return redirect(f"/users/{user.id}/profile")


@app.route('/users/<id>/update_profile', methods=["POST"])
def update_user_profile(id):
    user = get_user(pool, {'id': id})
    new_name = request.form.get('new_name')
    new_email = request.form.get('new_email')


@app.route('/signin', methods=['POST', "GET"])
def login_handler():
    if request.method == 'GET':
        return render_template('signin.html')
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = md5(request.form.get(
            "password").strip().encode("utf-8")).hexdigest()
        query = "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s"
        # run query func, get bool
        if True:
            # return redirect("/")
            pass
        return render_template("signin.html", message="Incorrect details")


@app.route('/signup', methods=['POST', "GET"])
def signup_handler():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == "POST":
        # check passwords
        password = md5(request.form.get(
            "password").strip().encode("utf-8")).hexdigest()
        confirm_password = md5(request.form.get(
            "confirm_password").strip().encode("utf-8")).hexdigest()
        if password != confirm_password:
            return render_template("signup.html", message="Passwords don't match. Try")

        # get remaining values
        email = request.form.get("email").strip()
        name = request.form.get("name").strip()
        is_host = request.form.get("is_host")
        if is_host is None:
            is_host = False
        else:
            is_host = True

        # run user query func, get result and check
        if True:
            # return redirect("/")
            pass
        return render_template("signup.html", message="Something went wrong, please try again!")


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
