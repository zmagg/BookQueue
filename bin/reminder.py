#!/usr/bin/env python

from app import mail, User, Book
from flask.ext.mail import Message


def send_reminders():
    users = User.query.filter(User.reviews_needed == True)
    for user in users:
        msg = Message("Time to review your latest batch of books!",
                      recipients=[user.email])
        books = Book.query.filter(Book.user_id == user.id,
                                    Book.review_needed == True).all()
        msg.body = ""
        for book in books:
            msg.body += book.info + "\n"
        msg.body += "\n(You can text DONE to 917-746-3273 or email \
            bookqueue@app10659070.mailgun.org with subject line \
            DONE to stop receiving these reminder emails."
        mail.send(msg)


if __name__ == '__main__':
    send_reminders()
