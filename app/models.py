from app import db, loginmanager
from flask_login import UserMixin

@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imagefile = db.Column(db.String(20), nullable=False, default='default.jpg')
    runefile = db.Column(db.String(20), nullable=False, default='emptybox.json')
    monsternames = db.Column(db.String(15000), nullable=False, default='')
    lockedrunes = db.Column(db.String(20), default=None)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
