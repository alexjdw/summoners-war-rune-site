from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import SelectField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import User, Guild


# Forms
class JsonForm(FlaskForm):
    jsonfile = FileField('jsonfile', validators=[FileRequired(), FileAllowed(['json'])])
    submit = SubmitField('Submit')


class RegForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already registered. Please pick\
                                  a new name.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.  Please pick\
                                  a new email.')


class GuildRegForm(FlaskForm):
    guildname = StringField('Guild Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_guildname(self, guildname):
        if Guild.query.filter_by(guildname=guildname.data).first().guildname is not None:
            raise ValidationError("Guildname already exists.")


class GuildInviteForm(FlaskForm):
    invitedplayerid = StringField('Invite Player', validators=[DataRequired()])
    submit = SubmitField('Submit')


class GuildBuildForm(FlaskForm):
    pass


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')

class MonsterSelectorForm(FlaskForm):
    evaluatorselector = SelectField('Build Type', validators=[DataRequired()])
    monsterselector = SelectField('Monster', validators=[DataRequired()])
    priset = SelectField('Primay Set', choices=[
        ("Energy", "Energy"),
        ("Guard", "Guard"),
        ("Swift", "Swift"),
        ("Blade", "Blade"),
        ("Rage", "Rage"),
        ("Focus", "Focus"),
        ("Endure", "Endure"),
        ("Fatal", "Fatal"),
        ("Despair", "Despair"),
        ("Vampire", "Vampire"),
        ("Violent", "Violent"),
        ("Nemesis", "Nemesis"),
        ("Will", "Will"),
        ("Shield", "Shield"),
        ("Revenge", "Revenge"),
        ("Destroy", "Destroy"),
        ("Fight", "Fight"),
        ("Determination", "Determination"),
        ("Enhance", "Enhance"),
        ("Accuracy", "Accuracy"),
        ("Tolerance", "Tolerance"),
        ])

    secset = SelectField('Secondary Set', choices=[
        ("Energy", "Energy"),
        ("Guard", "Guard"),
        ("Blade", "Blade"),
        ("Focus", "Focus"),
        ("Endure", "Endure"),
        ("Nemesis", "Nemesis"),
        ("Will", "Will"),
        ("Shield", "Shield"),
        ("Revenge", "Revenge"),
        ("Destroy", "Destroy"),
        ("Fight", "Fight"),
        ("Determination", "Determination"),
        ("Enhance", "Enhance"),
        ("Accuracy", "Accuracy"),
        ("Tolerance", "Tolerance"),
        ])

    donebutton = SubmitField("Done!")
    removebutton = SubmitField("Remove")
    addbutton = SubmitField("Add")

    mons = {}

    def add_mon(self, mon, eval_func_name, eval_func_display, pri, sec):
        self.mons[mon] = (eval_func_name, eval_func_display, pri, sec)

    def remove_mon(self, mon):
        if mon in self.mons.keys():
            del self.mons[mon]
