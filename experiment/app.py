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
           'results': {}}
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
    yes = None
    no = None
    user_id = current_user.get_username()
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

@app.route('/tree', methods=['GET'])
def tree():
    return render_template('tree.html')





if __name__ == '__main__':
    app.run(debug=True)
