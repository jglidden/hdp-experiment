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

with open('key.json') as f:
    EXPERIMENT_KEY = json.load(f)


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


@app.route('/exp')
@login_required
def exp():
    user_id = current_user.get_username()
    label = EXPERIMENT_KEY.keys()[0]
    img = 'stimuli/fruit-6-57.png'
    correct = False
    return render_template('experiment.html', label=label, img=img, correct=correct)





if __name__ == '__main__':
    app.run(debug=True)
