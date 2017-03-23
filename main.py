from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


app = Flask(__name__)



@app.route("/form", methods=["POST", "GET"])
def userForm():
    if request.method == "POST":
        return app.send_static_file('get_rating.html')
    else:
        return app.send_static_file('user_form.html')


@app.route("/perfer", methods=["POST", "GET"])
def getRating():
    if request.method == "POST":
        if request.form['button'] == 'Like':
            print('like')
            return app.send_static_file('get_rating.html')
        elif request.form['button'] == 'Dislike':
            print('dislike')
            return app.send_static_file('get_rating.html')
        else:
            print('OTHER')
            return app.send_static_file('get_rating.html')

    else:
        return app.send_static_file('get_rating.html')


app.run()

