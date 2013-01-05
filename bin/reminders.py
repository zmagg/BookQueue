#!/usr/bin/env python

import os
from app import User, Book
from flask import Flask
from flask.ext.mail import Mail, Message


app = Flask(__name__)
app.config.update(
    MAIL_SERVER=os.environ.get('MAILGUN_SMTP_SERVER', 'smtp.mailgun.org'),
    MAIL_PORT=os.environ.get('MAILGUN_SMTP_PORT', 587),
    MAIL_USERNAME=os.environ.get('MAILGUN_SMTP_LOGIN', None),
    MAIL_PASSWORD=os.environ.get('MAILGUN_SMTP_PASSWORD', None)
    )

subject_line = "Time to review your latest batch of books!"
reminder_line = "\n(You can text DONE to 917-746-3273 or email \
        bookqueue@app10659070.mailgun.org with subject line \
        DONE to stop receiving these reminder emails."

for user in User.query.filter(User.reviews_needed == True).all():
    msg = Message(subject_line, recipients=[user.email], sender="bookqueue@app10659070.mailgun.org")
    msg.body = ""
    books = Book.query.filter(Book.user_id == user.id,
                                Book.review_needed == True).all()
    for book in books:
        msg.body += book.info + "\n"
    msg.body += reminder_line
    Mail(app).send(msg)
