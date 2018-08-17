from app import db, loginmanager
from sqlalchemy import ForeignKey
from flask_login import UserMixin

@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Guild(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    __player_ids__ = db.Column(db.String(10000))

    def getPlayerNames():
        pass

    def getPlayerCount():
        pass

    def __repr__(self):
        return f"Guild {self.guildname}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imagefile = db.Column(db.String(20), nullable=False, default='default.jpg')
    runefile = db.Column(db.String(20), nullable=False, default='emptybox.json')
    monsternames = db.Column(db.String(15000), nullable=False, default='')
    lockedrunes = db.Column(db.String(20), default=None)
    password = db.Column(db.String(60), nullable=False)
    guild = db.Column(db.String, ForeignKey("guild.id"))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
