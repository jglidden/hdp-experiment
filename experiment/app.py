import os
from experiment import exp as experiment
from flask import *
from flask.ext.login import (LoginManager,
                             login_required,
                             UserMixin,
                             login_user,
                             logout_user,
                             current_user)
from flask.ext.sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.secret_key = 'somethingverysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATASTORE')
db = SQLAlchemy(app)

from logging import StreamHandler
app.logger.addHandler(StreamHandler())


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

BLOCKS = 3
BLOCKSIZE = len(experiment.ALL_IMGS)/BLOCKS
USERS = {}

# Database models
class Participant(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    username = db.Column(db.String(128))
    debriefed = db.Column(db.Boolean)
    sessions = db.relationship('Session', backref='participant')
    current_session = db.relationship('Session', uselist=False)

    def __init__(self, username):
        self.username = username
        self.debriefed = False
        self.current_session = Session(self.id)

    def __repr__(self):
        return '<Participant %r>' %self.username


class Session(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    img_index = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    incorrect = db.Column(db.Integer)
    participant_id = db.Column(db.String(128), db.ForeignKey('participant.id'))

    def __init__(self, participant):
        self.participant = participant
        self.img_index = 0
        self.correct = 0
        self.incorrect = 0


# User object
class User(UserMixin):
    def __init__(self, participant):
        self.participant = participant
    
    def get_username(self):
        return self.participant.username

    def set_debriefed(self, val):
        self.participant.debriefed = val
        db.session.commit()

    def is_debriefed(self):
        return self.participant.debriefed

    def get_id(self):
        return self.participant.id

    def check_password(self, password):
        return True

    def get_current_pair(self):
        current_session = self.participant.current_session
        img_index = current_session.img_index
        img = experiment.ALL_IMGS[img_index]
        label = experiment.gen_label(img)
        block_index = img_index / BLOCKSIZE + 1
        local_index = img_index % BLOCKSIZE + 1
        return label, img, local_index, block_index

    def advance_pair(self):
        current_session = self.participant.current_session
        current_session.img_index += 1
        db.session.commit()

    def finish_session(self):
        new_session = Session(self.participant)
        self.participant.current_session = new_session
        db.session.commit()



@login_manager.user_loader
def get_user(userid):
    participant = Participant.query.filter_by(id=userid).first()
    if participant is None:
        return None
    else:
        return User(participant)


def get_user_by_username(username):
    participant = Participant.query.filter_by(username=username).first()
    if participant is None:
        return None
    else:
        return User(participant)


def create_user(username):
    participant = Participant(username)
    db.session.add(participant)
    db.session.commit()
    return User(participant)


@app.route('/')
def root():
    return redirect(url_for('user'))


@app.route('/user')
@login_required
def user():
    username = current_user.get_username()
    new = True if not current_user.is_debriefed() else None
    return render_template('user.html', username=username, new=new)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' not in request.form:
            return redirect(url_for('login'))
        user = get_user_by_username(request.form['username'])
        if user is None:
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for(request.args.get('next') or 'exp'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form.get('username').strip()
        existing_user = get_user_by_username(username)
        if existing_user:
            return render_template('register.html', username_collision=True)
        user = create_user(username)
        login_user(user, remember=True)
        return redirect(url_for('user'))


@app.route('/exp', methods=['GET', 'POST'])
@login_required
def exp():
    current_user.set_debriefed(True)
    user_id = current_user.get_username()
    label, img, pair_index, block_index = current_user.get_current_pair()
    response = None
    if request.method == 'GET':
        correct = None
    elif request.method == 'POST':
        label = request.form.get('label')
        input = request.form['res'] == '1'
        response = request.form['res']
        actual = experiment.check_pair(label, img)
        correct = (input == actual)
        current_user.advance_pair()
    print response, type(response)
    return render_template(
        'experiment.html',
        label=label,
        img=img,
        correct=correct,
        res=response,
        pair_index=pair_index,
        block_size=BLOCKSIZE,
        block_index=block_index,
        block_count=BLOCKS)

@app.route('/tree', methods=['GET', 'POST'])
def tree():
    if request.method == 'POST':
        links = request.form.get('links')
        return redirect(url_for('results'))
    return render_template('tree.html')

@app.route('/results', methods=['GET'])
def results():
    return 'hi!'







if __name__ == '__main__':
    app.run(debug=True)
