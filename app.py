import os
from flask import Flask, request
import twilio.twiml
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
from random import randrange
import re


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL'],
    MAIL_SERVER=os.environ.get('MAILGUN_SMTP_SERVER', 'smtp.mailgun.org'),
    MAIL_PORT=os.environ.get('MAILGUN_SMTP_PORT', 587),
    MAIL_USERNAME=os.environ.get('MAILGUN_SMTP_LOGIN', None),
    MAIL_PASSWORD=os.environ.get('MAILGUN_SMTP_PASSWORD', None),
    DEFAULT_MAIL_SENDER="bookqueue@app10659070.mailgun.org"
    )
db = SQLAlchemy(app)
mail = Mail(app)


@app.route("/sms", methods=['GET', 'POST'])
def sms():
    from_number = request.values.get('From', None)
    user = find_or_create_user(from_number)
    text_content = request.form['Body'].lower()

    if re.search("email:", text_content):
        update_user_email(user, text_content)
        message = "Your email has been saved."
    elif text_content == 'eob':
        mark_end_of_batch(user)
        message = "Batch marked complete and ready for reviews."
        if not user.email:
            message += ("Please register an email address to receive"
                "reminders, by texting email:you@yourdomain.com")
    elif text_content == 'done':
        mark_batch_reviews_done(user)
        message = "Reviews for this batch marked complete."
    elif text_content == 'list':
        message = booklist_message(user)
    else:
        add_new_book(user, request.form['Body'])
        message = "Your book has been added."

    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)


# email routes


@app.route("/book", methods=['GET', 'POST'])
def book():
    user = find_user_from_email_headers(request)
    if user:
        add_new_book(user, request.form['body-plain'].split('\n', 1)[0])
        if user.email:
            message = Message("Your book has been added.",
                                recipients=[user.email])
            mail.send(message)
    return 'ok'


@app.route("/eob", methods=['GET', 'POST'])
def eob():
    user = find_user_from_email_headers(request)
    if user:
        mark_end_of_batch(user)
        if user.email:
            message_text = "Batch marked complete and ready for reviews. \
                (You can text DONE to 917-746-3273 or email \
                bookqueue@app10659070.mailgun.org with subject line \
                DONE to stop receiving these reminder emails.)"
            message = Message(message_text, recipients=[user.email])
            mail.send(message)
    return 'ok'


@app.route("/done", methods=['GET', 'POST'])
def done():
    user = find_user_from_email_headers(request)
    if user:
        mark_batch_reviews_done(user)
        if user.email:
            message = Message("Reviews for this batch marked complete.",
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


def add_new_book(user, book_info):
    book = Book(user.id, book_info)
    db.session.add(book)
    if ready_for_new_batch_to_review(user):
        mark_end_of_batch(user)
    db.session.commit()


def booklist_message(user):
    batch_books = Book.query.filter(Book.user_id == user.id,
                                            Book.review_needed == True).all()
    non_batch_books = Book.query.filter(Book.user_id == user.id,
                                            Book.review_needed == None).all()
    msg = ""
    if len(batch_books) > 0:
        msg += "Books in your latest complete batch waiting for reviews: \n"
        for book in batch_books:
            msg += book.info + " \n"
        msg += "\n"
    msg += "Books not yet batched/waiting for reviews: \n"
    for book in non_batch_books:
        msg += book.info + " \n"
    return msg


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


def mark_batch_reviews_done(user):
    books = Book.query.filter(Book.user_id == user.id,
                                Book.review_needed == True).all()
    for book in books:
        db.session.delete(book)
    user.reviews_needed = None
    db.session.commit()


def mark_end_of_batch(user):
    books = Book.query.filter(Book.user_id == user.id).all()
    for book in books:
        book.review_needed = True
    user.reviews_needed = True
    db.session.commit()


def ready_for_new_batch_to_review(user):
    db.session.commit()
    if user.reviews_needed:
        return False
    else:
        book_count = int(Book.query.filter(Book.user_id == user.id).count())
        minimum_books_needed_for_eob = 6 + randrange(7)
        return book_count >= minimum_books_needed_for_eob


def update_user_email(user, text_content):
    user.email = re.search("(?<=email:).+", text_content).group(0)
    db.session.commit()


# models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    reviews_needed = db.Column(db.Boolean, nullable=True)

    def __init__(self, phonenumber, email):
        self.phonenumber = phonenumber
        self.email = email

    def __repr__(self):
        return '<phone_number %r>' % self.phonenumber


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    info = db.Column(db.String(240))
    review_needed = db.Column(db.Boolean, nullable=True)

    def __init__(self, user_id, info):
        self.user_id = user_id
        self.info = info

    def __repr__(self):
        return '<info %r>' % self.info


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port)
