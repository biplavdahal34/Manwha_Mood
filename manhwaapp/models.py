from manhwaapp import app, db
from flask_login import UserMixin
from manhwaapp import login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable = False)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


class Manhwa(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    cover_image = db.Column(db.String)
    title = db.Column(db.String, nullable = False)
    genre = db.Column(db.String, nullable = False)
    ratings_number  = db.Column (db.Integer, nullable = False)
    rating_text = db.Column(db.String)

class MYmanhwalist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    manhwa_id = db.Column(db.Integer, db.ForeignKey('manhwa.id'), nullable = False)
    my_review_number = db.Column(db.Integer, nullable = False)
    my_review_text = db.Column(db.String)