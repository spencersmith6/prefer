from flask import Flask, request, render_template, redirect, url_for
import uuid
import numpy as np

app = Flask(__name__)

products = {'bde42acfb0cb47029837fec8ee577da4': ['plate', 'crate_and_barrel', 'white'],
            'cd5660f952ed44139257d4dac01e13bf': ['silverware', 'crate_and_barrel', 'silver'],
            'ed4790d2de904199b392353e4fc72848': ['braclet', 'urban_outfitter', 'leather'],
            '34d16774f5b14ba2ac623d71c04bf46a': ['shoes', 'nike', 'white']}

users = {'faac231bc26047719e7ef9961bfe7275': ['John Smith', 'male', 27],
         '8e9f1079e37147369664ad0024cea599': ['Jane Roberts', 'male', 29]}

ratings = {}

session_user_id = None # TODO: this should be replaced with write to / read from RDS

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file('user_form.html')


@app.route("/user", methods=["POST"])
def user_form():
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']

    global session_user_id # TODO: remove and replace with RDS

    session_user_id = uuid.uuid4().hex

    users[session_user_id] = [name, gender, int(age)] # TODO: write to RDS
    print(users)

    return redirect(url_for('prefer'))

@app.route("/prefer", methods=["POST", "GET"])
def prefer():

    if request.method == "GET": # first time on page
        product = products.items()[0]
        product_id = product[0]
        product_name = product[1][0]
        return render_template('prefer.html', product_name=product_name, product_id=product_id)  # TODO: should be the default item

    else:
        rating = request.form['rating']
        product_id = request.form['id']
        print rating
        print product_id

        ratings[(session_user_id, product_id)] = rating # TODO: write to RDS

        # TODO: this should be generated using backservice
        new_product = products.items()[1]
        new_product_id = new_product[0]
        new_product_name = new_product[1][0]

        return render_template('prefer.html', product_name=new_product_name, product_id=new_product_id)


app.run()

