import os
from experiment import exp as exper
from flask import *
from flask.ext.login import (LoginManager,
                             login_required,
                             UserMixin,
                             login_user,
                             logout_user,
                             current_user)
from flask.ext.sqlalchemy import SQLAlchemy
from boto.mturk.connection import MTurkConnection
import logging
import uuid
import datetime
import markdown

app = Flask(__name__)
app.secret_key = 'somethingverysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://jglidden:rottin153@mysql.cocosci.berkeley.edu/treehdpfruit')
app.config['ACCESS_ID'] = os.environ.get('AWS_ACCESS_KEY', 'AKIAJGBULS6Q3DXYVK4Q')
app.config['SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY', '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')
app.config['AWS_HOST'] = 'mturk.com'

mtc = MTurkConnection(
        aws_access_key_id=app.config['ACCESS_ID'],
        aws_secret_access_key=app.config['SECRET_KEY'],
        host=app.config['AWS_HOST'])
QUALIFICATION_ID = '3SLCM7XLWH8WO61VD7YZPK4Q3U9T69'
db = SQLAlchemy(app)

from logging import StreamHandler
app.logger.addHandler(StreamHandler())


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

QUIZ = int(os.environ.get('COCO_QUIZ', '1')) != 0
TREE_ON_BLOCK = True
#DEBUG = os.environ.get('DEBUG_EXPERIMENT')
DEBUG = False
if DEBUG:
    IMG_PER_SESSION = 6
    BLOCKS = 2
else:
    IMG_PER_SESSION = 200
    BLOCKS = 4
BLOCKSIZE = IMG_PER_SESSION/BLOCKS
USERS = {}

# Database models
_part_session = db.Table('part_session',
        db.Column('participant_id', db.String(128), db.ForeignKey('participant.id')),
        db.Column('session_id', db.String(128), db.ForeignKey('session.id'))
)

_session_block = db.Table('session_block',
        db.Column('session_id', db.String(128), db.ForeignKey('session.id')),
        db.Column('block_id', db.String(128), db.ForeignKey('block.id'))
)

_block_response = db.Table('block_response',
        db.Column('block_id', db.String(128), db.ForeignKey('block.id')),
        db.Column('response_id', db.String(128), db.ForeignKey('response.id'))
)

_session_tree = db.Table('session_tree',
        db.Column('session_id', db.String(128), db.ForeignKey('session.id')),
        db.Column('tree_id', db.String(128), db.ForeignKey('tree.id'))
)

_tree_link = db.Table('tree_link',
        db.Column('tree_id', db.String(128), db.ForeignKey('tree.id')),
        db.Column('link_id', db.String(128), db.ForeignKey('link.id'))
)


class Participant(db.Model):
    __tablename__ = 'participant'

    id = db.Column(db.String(128), primary_key=True)
    username = db.Column(db.String(128))
    debriefed = db.Column(db.Boolean)
    tree_debriefed = db.Column(db.Boolean)
    on_break = db.Column(db.Boolean)
    sessions = db.relationship('Session', secondary=_part_session, backref='participant')
    current_session_id = db.Column(db.String(128), db.ForeignKey('session.id'))
    created_at = db.Column(db.DateTime)

    def __init__(self, username, id=None):
        if id is None:
            self.id = str(uuid.uuid4())
        self.username = username
        self.created_at = datetime.datetime.now()
        self.debriefed = False
        self.tree_debriefed = False
        self.on_break = False
        self.current_session = None 

    def __repr__(self):
        return '<Participant %r>' %self.username



class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.String(128), primary_key=True)
    img_index = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    incorrect = db.Column(db.Integer)
    session_participant = db.relationship('Participant', uselist=False, backref='current_session')
    blocks = db.relationship('Block', secondary=_session_block)
    current_block_id = db.Column(db.String(128), db.ForeignKey('block.id'))
    created_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    assignment_id = db.Column(db.String(128))
    submit_to = db.Column(db.String(128))
    hit_id = db.Column(db.String(128))
    img = db.Column(db.String(128))
    label = db.Column(db.String(128))
    trees = db.relationship('Tree', secondary=_session_tree, backref='session')

    def __init__(self, participant, assignment_id, submit_to, hit_id):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.session_participant = participant
        self.img_index = 0
        self.correct = 0
        self.incorrect = 0
        new_block = Block(self)
        self.blocks.append(new_block)
        self.current_block = new_block
        self.assignment_id = assignment_id
        self.submit_to = submit_to
        self.hit_id = hit_id
        label, img = exper.gen_pair()
        self.label = label
        self.img = img


class Block(db.Model):
    __tablename__ = 'block'

    id = db.Column(db.String(128), primary_key=True)
    block_session = db.relationship('Session', uselist=False, backref='current_block')
    correct = db.Column('correct', db.Integer)
    incorrect = db.Column('incorrect', db.Integer)
    created_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    responses = db.relationship('Response', secondary=_block_response, backref='block')

    def __init__(self, session):
        self.id = str(uuid.uuid4())
        self.session = session
        self.created_at = datetime.datetime.now()
        self.correct = 0
        self.incorrect = 0

class Response(db.Model):
    __tablename__ = 'response'

    id = db.Column(db.String(128), primary_key=True)
    stimulus = db.Column(db.String(128))
    label = db.Column(db.String(128))
    response = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, block, stimulus, label, response):
        self.id = str(uuid.uuid4())
        self.block_response = block
        self.stimulus = stimulus
        self.label = label
        self.created_at = datetime.datetime.now()


class Tree(db.Model):
    __tablename__ = 'tree'
    id = db.Column(db.String(128), primary_key=True)
    links = db.relationship('Link', secondary=_tree_link, backref='tree')
    created_at = db.Column(db.DateTime)

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()


class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.String(128), primary_key=True)
    source = db.Column(db.Integer)
    target = db.Column(db.Integer)

    def __init__(self, source, target):
        self.id = str(uuid.uuid4())
        self.source = source
        self.target = target



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

    def set_tree_debriefed(self, val):
        self.participant.tree_debriefed = val
        db.session.commit()

    def is_tree_debriefed(self):
        return self.participant.tree_debriefed

    def get_break(self):
        return self.participant.on_break

    def set_break(self, val):
        self.participant.on_break = val
        db.session.commit()

    def get_id(self):
        return self.participant.id

    def check_password(self, password):
        return True

    def get_current_assignment_id(self):
        return self.participant.current_session.assignment_id

    def get_submit_to(self):
        return self.participant.current_session.submit_to
    
    def get_current_session(self):
        return self.participant.current_session

    def get_current_pair(self):
        current_session = self.participant.current_session
        img_index = current_session.img_index
        label = current_session.label
        img = current_session.img
        block_index = img_index / BLOCKSIZE + 1
        local_index = img_index % BLOCKSIZE + 1
        return label, img, local_index, block_index

    def advance_pair(self):
        current_session = self.participant.current_session
        current_session.img_index += 1
        img_index = current_session.img_index
        label, img = exper.gen_pair()
        current_session.label = label
        current_session.img = img
        if img_index % BLOCKSIZE == 0:
            self.participant.on_break = True
        db.session.commit()

    def update_correct(self, correct):
        current_session = self.participant.current_session
        if correct:
            current_session.correct += 1
            current_session.current_block.correct += 1
        else:
            current_session.incorrect += 1
            current_session.current_block.incorrect += 1
        db.session.commit()

    def add_response(self, stimulus, label, res):
        current_block = self.participant.current_session.current_block
        response = Response(
                current_block,
                stimulus,
                label,
                res)
        db.session.add(response)
        db.session.commit()

    def add_tree(self, links):
        current_session = self.participant.current_session
        tree = Tree()
        current_session.trees.append(tree)
        db.session.add(tree)
        for link in links:
            new_link = Link(link['source']['id'], link['target']['id'])
            tree.links.append(new_link)
            db.session.add(new_link)
        db.session.commit()

    def create_new_session(self, assignment_id, submit_to, hit_id):
        new_session = Session(self.participant, assignment_id, submit_to, hit_id)
        self.participant.sessions.append(new_session)
        self.participant.current_session = new_session
        db.session.add(new_session)
        db.session.commit()

    def finish_session(self):
        self.participant.current_session.finished_at = datetime.datetime.now()
        self.participant.current_session = None
        self.participant.on_break = False
        db.session.commit()

    def create_new_block(self):
        new_block = Block(self.participant.current_session)
        self.participant.current_session.blocks.append(new_block)
        self.participant.current_session.current_block = new_block
        db.session.add(new_block)
        db.session.commit()

    def finish_block(self):
        self.participant.current_session.current_block.finished_at = datetime.datetime.now()
        self.create_new_block()

    def get_best(self):
        sessions = self.participant.sessions
        current_session = self.participant.current_session
        sessions = [sess for sess in self.participant.sessions if sess is not current_session]
        if sessions:
            return max(sessions, key=lambda sess: sess.correct)
        else:
            return current_session

    def get_scores(self):
        sessions = self.participant.sessions
        current_session = self.participant.current_session
        sessions = [sess for sess in self.participant.sessions if sess is not current_session]
        sessions.sort(key=lambda sess: sess.finished_at)
        return [(sess.correct, sess.incorrect) for sess in sessions]





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
    logout_user()
    worker_id = request.args.get('workerId')
    assignment_id = request.args.get('assignmentId')
    hit_id = request.args.get('hitId')
    submit_to = request.args.get('turkSubmitTo')
    if worker_id:
        user = get_user_by_username(worker_id)
        if user:
            login_user(user, remember=True)
        else:
            user = create_user(worker_id)
            login_user(user, remember=True)
            try:
                mtc.assign_qualification(QUALIFICATION_ID, worker_id, value=0)
            except:
                pass
        if user.get_current_session() == None:
            user.create_new_session(assignment_id, submit_to, hit_id)
    return redirect(url_for('exp'))


def get_diffsign(diffbest):
    if diffbest < 0:
        diffsign = 'negative'
    elif diffbest > 0:
        diffsign = 'positive'
    else:
        diffsign = 'equal'
    return diffsign

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


#@app.route('/logout')
#@login_required
#def logout():
#    logout_user()
#    return redirect(request.args.get('next') or url_for('login'))


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
def exp():
    if not current_user.is_authenticated():
        return render_template(
                'experiment.html',
                img=exper.ALL_IMGS[0],
                label=exper.LABELS_BY_CAT['1'][0],
                preview=True,
                score=0.)
    new = True if not current_user.is_debriefed() else None
    current_user.set_debriefed(True)
    user_id = current_user.get_username()
    if current_user.participant.current_session.img_index == IMG_PER_SESSION:
        return redirect(url_for('tree'))

    if current_user.get_break():
        current_user.finish_block()
        current_user.set_break(False)
        if TREE_ON_BLOCK:
            return redirect(url_for('tree'))
        part = current_user.participant
        if not QUIZ:
            return render_template('finish_block.html', quiz=False)
        best_session = current_user.get_best()
        score = part.current_session.correct
        block_count = len(part.current_session.blocks)
        best_blocks = sorted([b for b in best_session.blocks if b.finished_at], key=lambda b: b.finished_at)[:block_count+1]
        if not best_blocks:
            diffsign = 'equal'
            diff = 0
        else:
            diffbest = score - sum([b.correct for b in best_blocks])
            diff = abs(diffbest)
            diffsign = get_diffsign(diffbest)
        return render_template(
                'finish_block.html',
                quiz=True,
                diffsign=diffsign,
                diff=diff,
                )
    label, img, pair_index, block_index = current_user.get_current_pair()
    response = None
    if request.method == 'GET':
        correct = None
    elif request.method == 'POST':
        label = request.form.get('label')
        if QUIZ:
            input = request.form['res'] == '1'
            response = request.form['res']
            actual = exper.check_pair(label, img)
            correct = (input == actual)
            current_user.update_correct(correct)
            current_user.add_response(img, label, response)
        current_user.advance_pair()
    part = current_user.participant
    if part.current_session.img_index == 0:
        current_score = 0.
    else:
        current_score = float(part.current_session.correct) / part.current_session.img_index
    if QUIZ:
        return render_template(
            'experiment.html',
            quiz=True,
            label=label,
            img=img,
            correct=correct,
            res=response,
            pair_index=pair_index,
            block_size=BLOCKSIZE,
            block_index=block_index,
            block_count=BLOCKS,
            new=new,
            score=current_score)
    else:
        current_user.advance_pair()
        return render_template(
            'experiment.html',
            quiz=False,
            label=label,
            img=img,
            new=new,
            block_size=BLOCKSIZE,
            block_index=block_index,
            block_count=BLOCKS)

@app.route('/tree', methods=['GET', 'POST'])
@login_required
def tree():
    if request.method == 'POST':
        links = json.loads(request.form.get('links'))
        current_user.add_tree(links)
        if current_user.participant.current_session.img_index == IMG_PER_SESSION:
            return redirect(url_for('results'))
        else:
            return redirect(url_for('exp'))
    new = True if not current_user.is_tree_debriefed() else None
    current_user.set_tree_debriefed(True)
    return render_template('tree.html', new=new)


@app.route('/tree_instructions', methods=['GET'])
@login_required
def tree_instructions():
    return render_template('tree_instructions.html')

@app.route('/experiment_instructions/<pageno>', methods=['GET'])
def experiment_instruction(pageno):
    pageno=int(pageno)
    nextpage = None
    if pageno < 6:
        nextpage = pageno + 1
    return render_template('experiment_instructions.html', pageno=pageno, nextpage=nextpage)

@app.route('/example_taxonomy/<id>', methods=['GET'])
def example_taxonomy(id):
    try:
        return exper.load_example(id)
    except IOError:
        abort(404)

@app.route('/results', methods=['GET'])
@login_required
def results():
    if not current_user.get_current_session():
        return redirect(url_for('root'))
    assignment_id = current_user.get_current_assignment_id()
    submit_base = current_user.get_submit_to()
    if submit_base:
        submit_to = os.path.join(current_user.get_submit_to(), 'mturk/externalSubmit')
    else:
        submit_to = '/'
    current_user.finish_session()
    worker_id = current_user.get_username()
    try:
        qualification_score = mtc.get_qualification_score(QUALIFICATION_ID, worker_id)
        mtc.update_qualification_score(QUALIFICATION_ID, worker_id, qualification_score+1)
    except:
        pass
    if QUIZ:
        scores = current_user.get_scores()
        corrects = [s[0] for s in scores]
        if len(corrects) > 1:
            diffbest = corrects[-1] - max(corrects[:-1])
            diff = abs(diffbest)
            diffsign = get_diffsign(diffbest)
        else:
            diffsign = 'equal'
            diff = 0
        return render_template(
                'results.html',
                quiz=True,
                diffsign=diffsign,
                diff=diff,
                sesscount=len(corrects),
                assignment_id=assignment_id,
                submit_to=submit_to)
    else:
        return render_template(
                'results.html',
                quiz=False,
                assignment_id=assignment_id,
                submit_to=submit_to)


@app.route('/scores', methods=['GET'])
@login_required
def scores():
    scores = current_user.get_scores()
    corrects = [{'i': str(i), 'correct': s[0]} for i, s in enumerate(scores)]
    return json.dumps(corrects)

@app.route('/results_plot', methods=['GET'])
@login_required
def results_plot():
    return render_template('results_plot.html')







if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
