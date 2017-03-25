from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
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


PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Perfer</title>
</head>
<body>
    <h1>What is your preference?</h1>
    <h3>%s</h3>
    <form action="/perfer" method=post enctype=multipart/form-data>
        <button type="submit" name = 'button' value = '1:%s'>Like</button>
        <button type="submit" name = 'button' value = '0:%s'>Dislike</button>

    </form>
</body>
</html>
'''



def gen_perfer_page():
    random_product_id = np.random.choice(list(products.keys()),1)[0]
    product =products[random_product_id][0]
    return PAGE_TEMPLATE %(product, random_product_id, random_product_id)


session_user_id = None
@app.route("/form", methods=["POST", "GET"])
def userForm():
    if request.method == "POST":
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        global session_user_id
        session_user_id = uuid.uuid4().hex
        users[session_user_id] = [name, gender, int(age)]
        page = gen_perfer_page()
        print(users)
        return page
    else:
        return app.send_static_file('user_form.html')


@app.route("/perfer", methods=["POST", "GET"])
def getRating():
    if request.method == "POST":
        rating_productid = request.form['button'].split(':')
        rating = int(rating_productid[0])
        product_id = rating_productid[1]
        print(rating_productid)
        ratings[(session_user_id, product_id)] = rating

        print(ratings)

        page = gen_perfer_page()
        return page



app.run()

