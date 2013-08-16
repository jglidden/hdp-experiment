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

DEBUG_BLOCKSIZE = 4
BLOCKS = 8
USERS = {}


class User(UserMixin):
    def __init__(self, doc):
        self.doc = doc
    
    def get_username(self):
        return self.doc['username']

    def get_id(self):
        return self.doc['username']

    def check_password(self, password):
        return True


@login_manager.user_loader
def get_user(username):
    doc = USERS.get(username)
    if doc is None:
        return None
    else:
        return User(doc)


def create_user(username):
    doc = {'username': username,
           'sessions': {'completed': [], 'session': create_session()}}
    USERS[username] = doc
    return User(doc)

def create_session():
    pairs = experiment.gen_pairs()
    blocks = []
    for i in xrange(0, len(l), n):
        blocks.append(pairs[i:i+BLOCKS][:DEBUG_BLOCKSIZE])
    return {'blocks': blocks}

def finish_session(user):
    user_doc = user.doc
    session = user_doc['session']
    completed = {
        'correct': session['correct'],
        'incorrect': session['incorrect']
    }
    user_doc['completed'].append(completed)
    new_session = create_session()
    user_doc['session'] = new_session
    return new_session

    

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
    yes = None
    no = None
    user_id = current_user.get_username()
    session = current_user.doc['sessions']['current']
    if session is None:
        session = create_session(current_user)
    if request.method == 'GET':
        correct = None
        label, img = experiment.gen_pair()
    elif request.method == 'POST':
        label = request.form.get('label')
        img = request.form.get('img')
        yes = ('yes' in request.form.keys())
        no = ('no' in request.form.keys())
        input = yes
        actual = experiment.check_pair(label, img)
        correct = (input == actual)
    return render_template(
        'experiment.html',
        label=label,
        img=img,
        correct=correct,
        yes=yes,
        no=no)

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
