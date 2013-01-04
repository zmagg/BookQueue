import os
from flask import Flask, request
import twilio.twiml
from flask.ext.sqlalchemy import SQLAlchemy
from random import randrange

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


#routes


@app.route("/sms", methods=['GET', 'POST'])
def sms():
    from_number = request.values.get('From', None)
    user = find_or_create_user(from_number)
    text_content = request.form['Body'].lower()

    if is_email(text_content):
        user.email = text_content
        message = "Your email has been saved."
    elif text_content == 'eob':
        mark_end_of_batch(user)
        message = "Batch marked complete."
    elif text_content == 'done':
        user.reviews_needed = False
        message = "Reviews for this batch marked complete."
    else:
        book = Book(user.id, text_content)
        db.session.add(book)
        if ready_for_new_batch_to_review(user):
            mark_end_of_batch(user)
        message = "Your book has been added."

    db.session.commit()

    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)


def find_or_create_user(from_number):
    db_results = User.query.filter(User.phonenumber == from_number)
    if len(db_results) > 0:
        return db_results[0]
    else:
        user = User('admin', 'none')
        db.session.add(user)
        db.session.commit()
        return user


def is_email(text_content):
    '@' in text_content and ' ' not in text_content


def mark_end_of_batch(user):
    books = Book.query.filter(Book.user_id == user.id)
    for book in books:
        book.review_needed = True
    user.reviews_needed = True


def ready_for_new_batch_to_review(user):
    db.session.commit()
    if user.reviews_needed == True:
        return False
    else:
        book_count = len(Book.query.filter(Book.user_id == user.id))
        return book_count >= (6 + randrange(6))


# models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    reviews_needed = db.Column(db.Boolean, default=False)

    def __init__(self, phonenumber, email):
        self.phonenumber = phonenumber
        self.email = email

    def __repr__(self):
        return '<phone_number %r>' % self.phonenumber


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    info = db.Column(db.String(240), unique=True)
    review_needed = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, info):
        self.user_id = user_id
        self.info = info

    def __repr__(self):
        return '<info %r>' % self.info


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
