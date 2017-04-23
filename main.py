from flask import Flask, request, render_template, redirect, url_for, jsonify, make_response
import uuid
from db_admin.sql_helper import getConn, getCur
from utils.db_utils import get_item_by_id, write_new_user_to_db, write_new_rating_to_db, check_if_user_in_db
import model.explore_or_exploit
import pickle

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file('index.html')


@app.route("/signup", methods=["GET"])
def signup(error=None):
    return render_template('signup.html', error=error)


@app.route("/login", methods=["GET"])
def login(error=None):
    return render_template('login.html', error=error)


@app.route("/post-signup", methods=["POST"])
def post_signup():

    # Get data from form
    print request.form
    user_id = request.form['username']
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']

    # open connection
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)

    # check whether user is in user database already
    in_db = check_if_user_in_db(cur, user_id)

    if in_db:
        # Return sign-up with error
        resp = signup(error='Username already exists.')
    else:
        # Set cookie as user ID
        resp = redirect(url_for('prefer'))
        resp.set_cookie('userID', user_id)

        # Write user data with session id to db
        conn = getConn('db_admin/creds.json')
        cur = getCur(conn)
        user = {'id': user_id, 'name': name, 'gender': gender, 'age': int(age)}
        print(user)
        write_new_user_to_db(cur, user)

    # close connection
    conn.commit()
    cur.close()
    conn.close()

    return resp


@app.route("/post-login", methods=["POST"])
def post_login():

    error = None

    # Get data from form
    print request.form
    user_id = request.form['username']

    # check that user is in user database
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    in_db = check_if_user_in_db(cur, user_id)
    conn.commit()
    cur.close()
    conn.close()

    if in_db:
        # Set cookie as user ID
        resp = redirect(url_for('prefer'))
        resp.set_cookie('userID', user_id)
        return resp
    else:
        return login(error='Invalid username.')


@app.route("/prefer", methods=["GET"])
def prefer():

    # check if the user has a cookie already, if not, create one
    if 'userID' not in request.cookies:
        user_id = str(uuid.uuid4().hex)
    else:
        user_id = request.cookies.get('userID')

    # get new item id from backend
    item_id = model.explore_or_exploit.get_next_item(user_id, le_item, nmf_model)

    # get item from the database
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    item = get_item_by_id(cur, item_id)
    conn.commit()
    cur.close()
    conn.close()

    # create response to client
    item_id = item['id']
    item_name = item['title']
    item_image = item['im_url']
    resp = make_response(render_template('prefer.html',
                           product_name=item_name,
                           product_id=item_id,
                           product_image=item_image))

    # set the cookie if it wasn't already there
    if 'userID' not in request.cookies:
        resp.set_cookie('userID', user_id)

    return resp


@app.route("/next_prefer", methods=["POST"])
def next_prefer():
    # define preference to rating dictionary
    preference_to_rating = {"Dislike": 0.0, "Like": 1.0}

    # get user swipe preference
    preference = request.form.get('preference', type=str)
    rating = preference_to_rating[preference]
    product_id = request.form.get('product_id', type=str)
    user_id = request.cookies.get('userID')
    print rating
    print product_id
    print user_id

    # open connection
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)

    # write to db
    write_new_rating_to_db(cur, user_id, product_id, rating)

    conn.commit()

    # get new item
    new_item_id = model.explore_or_exploit.get_next_item(user_id, le_item, nmf_model)
    new_item = get_item_by_id(cur, new_item_id)

    conn.commit()

    print new_item

    # close connection
    cur.close()
    conn.close()

    return jsonify(product_name=new_item['title'],
                   product_id=new_item['id'],
                   product_image=new_item['im_url'])

if __name__ == '__main__':

    # load pretrained models
    with open('data/nmf.pkl', 'rb') as fid:
        nmf_model = pickle.load(fid)

    with open('data/item_encoder.pkl', 'rb') as fid:
        le_item = pickle.load(fid)

    app.run(host='0.0.0.0')


