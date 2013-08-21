from experiment import exp as experiment
from flask import *
from flask.ext.login import (LoginManager,
                             login_required,
                             UserMixin,
                             login_user,
                             logout_user,
                             current_user)

app = Flask(__name__)
app.secret_key = 'somethingverysecret'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

DEBUG_BLOCKSIZE = 2
BLOCKS = 3
USERS = {}


class User(UserMixin):
    def __init__(self, doc):
        self.doc = doc
        if self.doc['sessions'] is None:
           doc['sessions'] = {'completed': [], 'current_session': self.create_session()}
           doc['block_index'] = 1
           doc['pair_index'] = 1
           doc['current_pair'] = doc['sessions']['current_session']['current_block'].pop()
    
    def get_username(self):
        return self.doc['username']

    def get_id(self):
        return self.doc['username']

    def check_password(self, password):
        return True

    def get_current_pair(self):
        doc = self.doc
        label, img = doc['current_pair']
        pair_index = doc['pair_index']
        block_index = doc['block_index']
        return label, img, pair_index, block_index

    def advance_pair(self):
        doc = self.doc
        session = doc['sessions']['current_session']
        if len(session['current_block']) == 0:
            doc['pair_index'] = 1
            if len(session['blocks']) == 0:
                doc['block_index'] = 1
                self.finish_session()
            else:
                session['current_block'] = session['blocks'].pop()
                doc['block_index'] = doc.get('block_index', 0) + 1
        else:
            doc['pair_index'] = doc.get('pair_index', 0) + 1
        doc['current_pair'] = doc['sessions']['current_session']['current_block'].pop()

    def finish_session(self):
        doc = self.doc
        session = doc['sessions']['current_session']
        completed = {
            'correct': session['correct'],
            'incorrect': session['incorrect']
        }
        doc['sessions']['completed'].append(completed)
        new_session = self.create_session()
        doc['sessions']['current_session'] = new_session

    def create_session(self):
        pairs = experiment.gen_pairs()
        blocks = []
        for i in xrange(0, len(pairs), BLOCKS+1):
            blocks.append(pairs[i:i+BLOCKS][:DEBUG_BLOCKSIZE])
        assert all([len(b) == DEBUG_BLOCKSIZE for b in blocks])
        assert len(blocks) == BLOCKS, '{} != {}'.format(len(blocks), BLOCKS)
        current = blocks.pop()
        return {'blocks': blocks,
                'current_block': current,
                'correct': 0,
                'incorrect': 0}



@login_manager.user_loader
def get_user(username):
    doc = USERS.get(username)
    if doc is None:
        return None
    else:
        return User(doc)


def create_user(username):
    doc = {'username': username, 'sessions': None}
    USERS[username] = doc
    return User(doc)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' not in request.form:
            return redirect(url_for('login'))
        user = get_user(request.form['username'])
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
        existing_user = get_user(username)
        if existing_user:
            return render_template('register.html', username_collision=True)
        user = create_user(username)
        login_user(user, remember=True)
        return redirect(url_for('exp'))


@app.route('/exp', methods=['GET', 'POST'])
@login_required
def exp():
    print 'DEBUG_BLOCKS', len(current_user.doc['sessions']['current_session']['blocks'])
    print 'DEBUG_BLOCK_SIZES', [len(b) for b in current_user.doc['sessions']['current_session']['blocks']]
    print 'DEBUG_CURRENT', len(current_user.doc['sessions']['current_session']['current_block'])
    yes = None
    no = None
    user_id = current_user.get_username()
    label, img, pair_index, block_index = current_user.get_current_pair()
    if request.method == 'GET':
        correct = None
    elif request.method == 'POST':
        label = request.form.get('label')
        img = request.form.get('img')
        yes = ('yes' in request.form.keys())
        no = ('no' in request.form.keys())
        input = yes
        actual = experiment.check_pair(label, img)
        correct = (input == actual)
        current_user.advance_pair()
    return render_template(
        'experiment.html',
        label=label,
        img=img,
        correct=correct,
        yes=yes,
        no=no,
        pair_index=pair_index,
        block_size=DEBUG_BLOCKSIZE,
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
