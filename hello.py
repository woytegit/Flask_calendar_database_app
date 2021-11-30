from os import name
from markupsafe import escape
from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for

app = Flask(__name__)

# @app.route('/')
# def index():
#     return redirect(url_for('wojtek'))

@app.route('/')
def my_form():
    return render_template('hello.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.capitalize()
    return render_template('hello_name.html', name=processed_text)

# @app.route('/login')
# def login():
#     abort(401)
#     print("this_is_never_executed()")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

# @app.route('/<name>')
# def hello(name=None):
#     return render_template('hello.html', name=name)

if __name__ == "__main__":
    app.debug = True
    app.run()

"""
$env:FLASK_APP = "hello"
$env:FLASK_ENV = "development"
flask run

This tells your operating system to listen on all public IPs.
$ flask run --host=0.0.0.0


"""
