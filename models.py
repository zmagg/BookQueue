from app import db


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
