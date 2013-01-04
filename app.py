import os
from flask import Flask, request
import twilio.twiml
from flask.ext.sqlalchemy import SQLAlchemy
from models import User, Book
from random import randrange

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


@app.route("/", methods=['GET', 'POST'])
def on_receive_text():
    from_number = request.values.get('From', None)
    user = find_or_create_user(from_number)
    text_content = request.form['Body'].lower()

    if is_email(text_content):
        user.email = text_content
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
        message = "Your book was added."

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


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
