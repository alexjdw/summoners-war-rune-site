import json

from app import db, loginmanager
from sqlalchemy import ForeignKey
from flask_login import UserMixin


@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Guild(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    guildname = db.Column(db.String(50), unique=True, nullable=False)
    __user_ids__ = db.Column(db.String(10000),
                             default='{ "ids": [] }',
                             nullable=False,
                             )

    def add_player(self, id):
        idjson = json.loads(self.__user_ids__)
        if id not in idjson['ids']:
            idjson['ids'].append(id)
        self.__user_ids__ = json.dumps(idjson)


    def remove_player(self, id):
        try:
            self.__user_ids__ = json.dumps(json.loads(self.__user_ids__)
                                           .remove(id))
        except ValueError:
            print("Guild.remove_player: ID not found... ", id)

    def get_player_names(self):
        names = []
        for id in json.loads(self.__user_ids__)['ids']:
            user = User.query.get(id)
            names.append(user.username)
        return names

    def getPlayerCount(self):
        return len(json.loads(self.__user_ids__)[ids])

    def __repr__(self):
        return self.guildname


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imagefile = db.Column(db.String(20), nullable=False, default='default.jpg')
    runefile = db.Column(db.String(20), nullable=False, default='emptybox.json')
    monsternames = db.Column(db.String(15000), nullable=False, default='')
    lockedrunes = db.Column(db.String(20), default=None)
    password = db.Column(db.String(60), nullable=False)
    guild = db.Column(db.String, ForeignKey("guild.id"), default=None)

    def guildname(self):
        if self.guild is not None:
            return Guild.query.get(self.guild).guildname

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
