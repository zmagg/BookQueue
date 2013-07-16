import os
from flask import Flask, request
import twilio.twiml
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
from random import randrange
import re

app = Flask(__name__)
db = SQLAlchemy(app)
mail = Mail(app)

def init_app():
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL'],
        MAIL_SERVER=os.environ.get('MAILGUN_SMTP_SERVER', 'smtp.mailgun.org'),
        MAIL_PORT=os.environ.get('MAILGUN_SMTP_PORT', 587),
        MAIL_USERNAME=os.environ.get('MAILGUN_SMTP_LOGIN', None),
        MAIL_PASSWORD=os.environ.get('MAILGUN_SMTP_PASSWORD', None),
        DEFAULT_MAIL_SENDER="bookqueue@app10659070.mailgun.org")

@app.route("/sms", methods=['GET', 'POST'])
def sms():
    from_number = request.values.get('From', None)
    user = find_or_create_user(from_number)
    text_content = request.form['Body'].lower()

    if re.search("email:", text_content):
        update_user_email(user, text_content)
        message = "Your email has been saved."
    elif text_content.startswith('list'):
        if text_content == 'list':
            message = list_categories(user)
        else:
            list_cat = text_content.strip('list').strip()
            message = list_books_for_category(user, list_cat)
    elif text_content.startswith('del'):
        book = text_content.strip('del').strip()
        mark_book_as_read(user, book)
        message = "deleted" + book
    else:
        book_and_cat = request.form['Body'].partition['***']
        add_new_boot(user, book_and_cat[0], book_and_cat[2].strip())
        message = "Your book has been added."

    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)

# email routes

# Category should be on second line if email.
@app.route("/book", methods=['GET', 'POST'])
def book():
    user = find_user_from_email_headers(request)
    if user:
        book_cat = request.form['body-plain'].split('\n')
        if book_cat.length > 1:
            add_new_book(user, book_cat[0], book_cat[1])
        else:
            add_new_book(user, book_cat[0], "NOCAT")
        if user.email:
            message = Message("Your book has been added.",
                                recipients=[user.email])
            mail.send(message)
    return 'ok'

@app.route("/list", methods=['GET', 'POST'])
def list():
    user = find_user_from_email_headers(request)
    if user and user.email:
        message = Message("Your current books in BookQueue",
                            recipients=[user.email])
        message.body = booklist_message(user)
        mail.send(message)
    return 'ok'

# shared functions for routes

def add_new_book(user, book_info, cat):
    if cat:
        book = Book(user.id, book_info, cat)
    else:
        book = Book(user.id, book_info, "NOCAT")
    db.session.add(book)
    db.session.commit()

def list_categories(user):
    cats = Set()
    msg = "Categories: "
    books = Book.query.filter(Book.user_id == user.id, Book.done == false).all()
    for book in books:
        cats.add(book.category)
    for cat in cats:
        msg += cat + "\n"
    return msg

def list_books_for_category(user, cat):
    msg = ""
    books = Book.query.filter(Book.user_id == user.id, Book.category == cat, Book.done == false)
        .all()
    for book in books:
        msg += book + "\n"
    return msg

def booklist_message(user):
    msg = ""
    books = Book.query.filter(Book.user_id == user.id, Book.done == false).all()
    for book in books:
        msg += book.info + "\n"
    return msg

def mark_book_as_read(user, book):
    book = Book.query.filter(Book.user_id == user.id, Book.info == book)
    book.done = True
    db.session.commit()

def find_or_create_user(from_number):
    query = User.query.filter(User.phonenumber == from_number)
    if int(query.count()) > 0:
        return query.first()
    else:
        user = User(from_number, None)
        db.session.add(user)
        db.session.commit()
        return user


def find_user_from_email_headers(request):
    from_email = request.form['sender'].lower()
    query = User.query.filter(User.email == from_email)
    if int(query.count()) > 0:
        return query.first()
    else:
        return None

def update_user_email(user, text_content):
    user.email = re.search("(?<=email:).+", text_content).group(0)
    db.session.commit()

# models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=True)

    def __init__(self, phonenumber, email):
        self.phonenumber = phonenumber
        self.email = email

    def __repr__(self):
        return '<phone_number %r>' % self.phonenumber


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    info = db.Column(db.String(240))
    category = db.Column(db.String(120))
    done = db.Column(db.Boolean)

    def __init__(self, user_id, info, category):
        self.user_id = user_id
        self.info = info
        self.category = category

    def __repr__(self):
        return '<info %r>' % self.info


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    init_app()
    app.run(host='0.0.0.0', port=port)
