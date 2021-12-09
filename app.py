from operator import and_, or_
from os import name
from markupsafe import escape
from flask import Flask, request, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import immediateload
from sqlalchemy.sql import text
from datetime import date, datetime

from sqlalchemy.sql.expression import distinct

# import pymysql
# from flask_bootstrap import Bootstrap
# from flask_wtf import FlaskForm
# from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField, DateField
# from wtforms.validators import InputRequired, Length, Regexp, NumberRange


app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
# app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# Flask-Bootstrap requires this line
# Bootstrap(app)

# the name of the database; add path if necessary
db_name = 'sockmarket.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

# each table in the database needs a class to be created for it
# db.Model is required - don't change it

# NOTHING BELOW THIS LINE NEEDS TO CHANGE
# this route will test the database connection and nothing more

# My variables
category_list = []
moder_guy = []
task_categories = {}
workers_dict = {}

# classes


class Kalendarz(db.Model):
    __tablename__ = 'Kalendarz'
    id = db.Column(db.Integer, primary_key=True)
    data_wydarzenia = db.Column(db.DateTime)
    kategoria = db.Column(db.String)
    opis = db.Column(db.Text)
    wstawil = db.Column(db.String)
    last_update = db.Column(db.DateTime)

    def __init__(self, data, kategoria, opis, wstawil):
        self.id = None
        self.data_wydarzenia = data
        self.kategoria = kategoria
        self.opis = opis
        self.wstawil = wstawil
        self.last_update = datetime.now()


class Pracownicy(db.Model):
    __tablename__ = 'Pracownicy'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String)
    nazwisko = db.Column(db.String)
    stanowisko = db.Column(db.String)
    uprawnienia = db.Column(db.Integer)

    def __init__(self, imie, nazwisko, stanowisko, uprawnienia):
        self.id = None
        self.imie = imie
        self.nazwisko = nazwisko
        self.stanowisko = stanowisko
        self.uprawnienia = uprawnienia


class Kategorie_zadan(db.Model):
    __tablename__ = 'Kategorie_zadan'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String)

    def __init__(self, nazwa):
        self.id = None
        self.nazwa = nazwa


class Stanowiska(db.Model):
    __tablename__ = 'Stanowiska'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String)

    def __init__(self, nazwa):
        self.id = None
        self.nazwa = nazwa


class Uprawnienia(db.Model):
    __tablename__ = 'Uprawnienia'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String)

    def __init__(self, nazwa):
        self.id = None
        self.nazwa = nazwa

# functions


def load_all_task_categories():
    categories_temp = Kategorie_zadan.query.order_by(
        Kategorie_zadan.nazwa).all()
    for item in categories_temp:
        task_categories[item.id] = item.nazwa
    return task_categories


def load_all_workers():
    workers_temp = Pracownicy.query.order_by(Pracownicy.nazwisko).all()
    for person in workers_temp:
        workers_dict[person.id] = {'imie': person.imie, 'nazwisko': person.nazwisko,
                                   'stanowisko': person.stanowisko, 'uprawienia': person.uprawnienia}
    return workers_dict


def setup_filter_lists():
    kalendarz = Kalendarz.query.all()
    for item in kalendarz:
        if item.kategoria not in category_list:
            category_list.append(item.kategoria)
        if item.wstawil not in moder_guy:
            moder_guy.append(item.wstawil)
    category_list.sort()
    moder_guy.sort()


################################################
# routes

@app.route('/')
def homepage():
    # if not len(task_categories):
    # setup_filter_lists()
    task_categories = load_all_task_categories()
    # print(load_all_task_categories())
    # print(load_all_workers())
    print('Lists updated')
    print(task_categories)
    return redirect('/database')


@app.route('/database', methods=['GET', 'POST'])
def testdb():
    print(request.method)
    try:
        if request.method == "POST":
            cat_filter = request.form["category_filter"]
            per_filter = request.form['modify_by_filter']
            if cat_filter == '' and per_filter != '':
                kalendarz = Kalendarz.query.order_by(
                    Kalendarz.data_wydarzenia).filter(
                    Kalendarz.wstawil == per_filter).all()
            elif per_filter == '' and cat_filter != '':
                kalendarz = Kalendarz.query.order_by(
                    Kalendarz.data_wydarzenia).filter(
                    Kalendarz.kategoria == cat_filter).all()
            elif per_filter == '' and cat_filter == '':
                kalendarz = Kalendarz.query.order_by(
                    Kalendarz.data_wydarzenia).all()
            else:
                kalendarz = Kalendarz.query.order_by(
                    Kalendarz.data_wydarzenia).filter(and_(
                        Kalendarz.kategoria == cat_filter, Kalendarz.wstawil == per_filter)).all()
        else:
            kalendarz = Kalendarz.query.order_by(
                Kalendarz.data_wydarzenia).all()
        for item in kalendarz:
            # Loop for date format visualisation corection
            item.data_wydarzenia = item.data_wydarzenia.strftime(
                "%Y-%m-%d")
            item.last_update = item.last_update.strftime(
                "%Y-%m-%d %H:%M:%S")
        return render_template('database.html',  output_data=kalendarz, kat_filter=task_categories, modified_by=moder_guy)

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/database_filter')
def use_filter():
    used_filter = None
    return redirect(url_for('/database', used_filter=used_filter))


@app.route('/database_add_new_event')
def add_event_form():
    workers_dict = load_all_workers()
    return render_template('database_add_new_event.html', modified_by=workers_dict)


@app.route('/database_update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event_to_update = Kalendarz.query.get_or_404(id)
    if request.method == "POST":
        event_to_update.data_wydarzenia = datetime.strptime(
            request.form['event_date'], "%Y-%m-%d")
        event_to_update.kategoria = request.form['category']
        event_to_update.opis = request.form['event_description']
        event_to_update.wstawil = request.form['user_name']
        event_to_update.last_update = datetime.now()
        try:
            db.session.commit()
            return redirect(url_for('.testdb'))
        except Exception as e:
            # e holds description of the error
            error_text = "<p>The error:<br>" + str(e) + "</p>"
            hed = '<h1>Something is broken.</h1>'
            return hed + error_text
    else:
        return render_template("database_update.html", event_to_update=event_to_update, modified_by=workers_dict)


@app.route("/database_delete/<int:id>")
def delete(id):
    event_to_delete = Kalendarz.query.get_or_404(id)
    try:
        db.session.delete(event_to_delete)
        db.session.commit()
        return redirect(url_for('.testdb'))

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/database_add_new_event', methods=['GET', 'POST'])
def add_to_database():
    data_wydarzenia = request.form['event_date']
    kategoria = request.form['category']
    opis = request.form['event_description']
    wstawil = request.form['user_name']
    # the data to be inserted into Sock model - the table, socks
    date_time_obj = datetime.strptime(
        data_wydarzenia, "%Y-%m-%d")
    record = Kalendarz(date_time_obj, kategoria, opis, wstawil)
    # Flask-SQLAlchemy magic adds record to database
    try:
        db.session.add(record)
        db.session.commit()
        load_all_workers()
        return redirect(url_for('.testdb'))  # trzeba podać nazwe funkcji
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/workers', methods=['GET', 'POST'])
def workers():
    pracownicy = Pracownicy.query.all()
    if request.method == "POST":
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        stanowisko = request.form['stanowisko']
        uprawnienia = request.form['uprawnienia']
        record = Pracownicy(imie, nazwisko, stanowisko, uprawnienia)
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            # e holds description of the error
            error_text = "<p>The error:<br>" + str(e) + "</p>"
            hed = '<h1>Something is broken.</h1>'
            return hed + error_text

    print(request.method)
    return render_template('workers.html', data_output=pracownicy)


@app.route("/worker_delete/<int:id>")
def delete_worker(id):
    worker_to_delete = Pracownicy.query.get_or_404(id)
    try:
        db.session.delete(worker_to_delete)
        db.session.commit()
        return redirect(url_for('workers'))

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/test')
def test():
    return render_template("base2.html")


@app.route('/about')
def about():
    # with db.engine.connect() as connection:
    # order_by = 'data_wydarzenia'
    # this is cool but doesn't work as I want
    # result = connection.execute(
    #     "   SELECT * \
    #         FROM kalendarz \
    #         ORDER BY {order_by}".format(order_by=order_by)).fetchall()
    # for item in result:
    # Loop for date format visualisation corection
    # 'LegacyRow' object does not support item assignment
    # item[1] = datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S.%f').strftime(
    #     "%Y-%m-%d")
    # item.last_update = item.last_update.strftime(
    #     "%Y-%m-%d %H:%M:%S")

    print(request.method)
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


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
