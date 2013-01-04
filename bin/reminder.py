#!/usr/bin/env python

import os
from flask.ext.mail import Mail, Message
from app import app, User, Book

app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER=os.environ.get('MAILGUN_SMTP_SERVER', 'smtp.mailgun.org'),
    MAIL_PORT=os.environ.get('MAILGUN_SMTP_PORT', 587),
    MAIL_USERNAME=os.environ.get('MAILGUN_SMTP_LOGIN', None),
    MAIL_PASSWORD=os.environ.get('MAILGUN_SMTP_PASSWORD', None)
    )

mail = Mail(app)


def send_reminders():
    users = User.query.filter(User.reviews_needed == True)
    for user in users:
        msg = Message("Time to review your latest batch of books!",
                      sender="dsucher@gmail.com",
                      recipients=[user.email])
        books = Book.query.filter(Book.user_id == user.id,
                                    Book.review_needed == True).all()
        msg.body = ""
        for book in books:
            msg.body += book.info + "\n"
        mail.send(msg)


if __name__ == '__main__':
    send_reminders()
