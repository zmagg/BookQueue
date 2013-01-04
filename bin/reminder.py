#!/usr/bin/env python

import os
from flask.ext.mail import Mail, Message
from app import app, User, Book


mail = Mail(app)


@app.route("/send_reminders")
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
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    send_reminders()
