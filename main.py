from flask import Flask, request, render_template, redirect, url_for, jsonify
import uuid
import numpy as np

app = Flask(__name__)

products = {'bde42acfb0cb47029837fec8ee577da4': ['plate', 'crate_and_barrel', 'white','https://images.crateandbarrel.com/is/image/Crate/MarinWhiteDinner10p5inSHF15/$web_setitem326$/160203171115/marin-white-dinner-plate.jpg'],
            'cd5660f952ed44139257d4dac01e13bf': ['silverware', 'crate_and_barrel', 'silver','https://images.crateandbarrel.com/is/image/Crate/BoulderPlacesetting5PcS13/$web_product_hero$&/150611091025/boulder-flatware.jpg'],
            'ed4790d2de904199b392353e4fc72848': ['bracelet', 'urban_outfitter', 'leather','http://images.urbanoutfitters.com/is/image/UrbanOutfitters/41548157_070_b?$mlarge$&defaultImage='],
            '34d16774f5b14ba2ac623d71c04bf46a': ['shoes', 'nike', 'white','http://images.nike.com/is/image/DotCom/511881_A_V2?&$img=511881_112_A_PREM&$PDP_HERO_M$']}

users = {'faac231bc26047719e7ef9961bfe7275': ['John Smith', 'male', 27],
         '8e9f1079e37147369664ad0024cea599': ['Jane Roberts', 'male', 29]}

ratings = {}

session_user_id = None # TODO: this should be replaced with write to / read from RDS


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file('user_form.html')


@app.route("/user", methods=["POST"])
def user_form():
    print request.form
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']

    global session_user_id # TODO: remove and replace with set cookie

    session_user_id = uuid.uuid4().hex

    users[session_user_id] = [name, gender, int(age)] # TODO: write to RDS
    print(users)

    return redirect(url_for('prefer'))


@app.route("/prefer", methods=["GET"])
def prefer():
    product = products.items()[0]
    product_id = product[0]
    product_name = product[1][0]
    product_image = product[1][3]
    return render_template('prefer.html',
                           product_name=product_name,
                           product_id=product_id,
                           product_image=product_image)  # TODO: should be the default item


@app.route("/next_prefer", methods=["POST"])
def next_prefer():
    rating = request.form.get('preference', type=str)
    product_id = request.form.get('product_id', type=str)
    print(rating)
    print(product_id)

    ratings[(session_user_id, product_id)] = rating # TODO: write to RDS

    # TODO: this should be generated using backend service
    new_product = products.items()[np.random.choice(range(len(products)))]
    new_product_id = new_product[0]
    new_product_name = new_product[1][0]
    new_product_image = new_product[1][3]

    return jsonify(product_name=new_product_name,
                   product_id=new_product_id,
                   product_image=new_product_image)


app.run(host='0.0.0.0')