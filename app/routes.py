import secrets
import os
import json

from flask import render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required

from app.models import User
from app.forms import JsonForm, RegForm, LoginForm, MonsterSelectorForm
from app import app, bcrypt, db

from opti.evaluations import MonsterEvaluator
from opti.runeimporter import RuneBox
from opti.suggest import suggestion_to_json
from opti.monsterbox import get_monster_names


# Routes
@app.route('/')
def home():
    return render_template('home.html',
                           page='home',
                           title='Home',
                           current_user=current_user,
                           )


def save_json(form_json):
    random_hex = secrets.token_hex(8)
    _, fext = os.path.splitext(form_json.filename)
    filename = random_hex + fext
    json_path = os.path.join(app.root_path, 'static', 'runeboxes', filename)
    form_json.save(json_path)
    return filename


@login_required
@app.route('/json', methods=['GET', 'POST'])
def upload():
    form = JsonForm()
    if form.validate_on_submit():
        json_filename = save_json(form.jsonfile.data)

        current_user.runefile = json_filename
        path = os.path.join(app.root_path, 'static', 'runeboxes',
                            current_user.runefile)
        names = get_monster_names(path)
        current_user.monsternames = json.dumps(names)

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('json.html',
                           page='upload',
                           title='Upload Monster Box',
                           form=form,
                           current_user=current_user,
                           )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = RegForm()
    if form.validate_on_submit():
        hashpw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashpw,
                    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('register.html',
                           form=form,
                           title='Register',
                           current_user=current_user,
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        redirect(url_for('home', uid=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('upload', uid=user.id))
        print("Login failed")

    return render_template('login.html',
                           form=form,
                           title='Log in',
                           current_user=current_user
                           )


@login_required
@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    form = MonsterSelectorForm()

    if not current_user.monsternames:
        return(redirect(url_for('home')))

    mons = set(json.loads(current_user.monsternames))
    mons.remove('Rainbowmon')
    mons.remove('UNKNOWN')

    evtypes = MonsterEvaluator(None).evaluation_types()
    evlabels = [type.replace('eval_', '').replace('_',' ').title() for type in evtypes]

    evchoices = list(zip(evtypes, evlabels))
    monchoices= list(zip(mons, mons))

    form.monsterselector.choices = monchoices
    form.evaluatorselector.choices = evchoices

    if form.validate_on_submit():
        if form.donebutton.data:  # Get runes for these monsters
            builds = {}
            stats = {}
            box = RuneBox(os.path.join(app.root_path, 'static', 'runeboxes', current_user.runefile))
            if current_user.lockedrunes:
                for rune_id in current_user.lockedrunes:
                    box.lock_rune(rune_id)
            for monster, selections in form.mons.items():
                js = json.loads(suggestion_to_json(box, monster, selections))
                builds[monster] = js['rune_ids']
                stats[monster] = js['stats']
                print(js['stats'])
                for rune_id in js['rune_ids']:
                    box.lock_rune(rune_id)

            return display_runes(builds, box, stats)

        if form.addbutton.data:
            form.add_mon(form.monsterselector.data,
                          form.evaluatorselector.data,
                          form.evaluatorselector.data.replace('eval_', '').replace('_',' ').title(),
                          form.priset.data,
                          form.secset.data,
                          )
        if form.removebutton.data:
            form.remove_mon(form.monsterselector.data)

    return render_template('selectmons.html',
                           form=form,
                           title="Choose Your Builds!",
                           current_user=current_user,
                           )

@app.route('/results')
def display_runes(builds, box, stats):
    for mon in builds:
        for index in range(len(builds[mon])):
            rune = box.get_rune(builds[mon][index])
            builds[mon][index] = rune.__str__()
            builds[mon][index] = builds[mon][index].replace('\n', '<br/>')
            builds[mon][index] = builds[mon][index].replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    return render_template('results.html', builds=builds, stats=stats)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
