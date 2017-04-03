from flask import Flask, request, render_template, redirect, url_for, jsonify
import uuid
import numpy as np
from db_admin.sql_helper import getConn, getCur
from utils.db_utils import get_item_by_id, write_new_user_to_db, write_new_rating_to_db
import random

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file('user_form.html')


@app.route("/user", methods=["POST"])
def user_form():

    # Get data from form
    print request.form
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']

    # Generate user ID and set cookie
    session_user_id = str(uuid.uuid4().hex)
    resp = redirect(url_for('prefer'))
    resp.set_cookie('userID', session_user_id)

    # Write user data with session id to db
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    user = {'id': session_user_id, 'name': name, 'gender': gender, 'age': int(age)}
    print(user)
    write_new_user_to_db(cur, user)
    conn.commit()
    cur.close()
    conn.close()

    return resp


@app.route("/prefer", methods=["GET"])
def prefer():

    # TODO: if this user doesn't have a cookie, set it and write to db with null values

    # get any item from the database
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    item = get_item_by_id(cur)
    conn.commit()
    cur.close()
    conn.close()

    # return to client
    item_id = item['id']
    item_name = item['title']
    item_image = item['im_url']
    return render_template('prefer.html',
                           product_name=item_name,
                           product_id=item_id,
                           product_image=item_image)


@app.route("/next_prefer", methods=["POST"])
def next_prefer():
    # define preference to rating dictionary
    preference_to_rating = {"Dislike": 0.0, "Like": 1.0}

    # get user swipe preference
    preference = request.form.get('preference', type=str)
    rating = preference_to_rating[preference]
    product_id = request.form.get('product_id', type=str)
    user_id = request.cookies['userID']
    print rating
    print product_id
    print user_id

    # write to db
    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    write_new_rating_to_db(cur, user_id, product_id, rating)
    conn.commit()
    cur.close()
    conn.close()

    # TODO: this should be generated using backend service, for now, it's random
    item_ids = ['0002200120','0002234572','0002237245','0002231832','0002218615']

    conn = getConn('db_admin/creds.json')
    cur = getCur(conn)
    new_item = get_item_by_id(cur, item_id=random.choice(item_ids))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(product_name=new_item['title'],
                   product_id=new_item['id'],
                   product_image=new_item['im_url'])

if __name__ == '__main__':
    app.run(host='0.0.0.0')