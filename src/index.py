from bottle import Bottle, run, template, request, redirect
from bottle_login import LoginPlugin
from passlib.hash import sha256_crypt as hasher

app = Bottle()
app.config['SECRET_KEY'] = 'secret'

login_plugin = app.install(LoginPlugin())


@login_plugin.load_user
def load_user_by_id(user_id):
    print("load_user_by_id")
    print(user_id)
    if user_id == 'foo':
        return {
            'name': 'Foo',
            'pwd': 'tTur0JLibvkcJbKGHJxd61MTHeEqFymUY3LzDACFsJ0',
            'salt': 'uauHYcJTDMilqcdX'
        }
    else:
        return None


@app.route('/')
def index():
    current_user = login_plugin.get_user()

    if current_user is None:
        return redirect('/login')

    return template('index', name=current_user["name"])


@app.route('/login')
def login():
    return template('login')


@app.route('/login', method='POST')
def do_login():
    # Implement login (you can check passwords here or etc)
    user_id = str(request.POST.get('username'))
    pwd = str(request.POST.get('password'))
    print(user_id)
    user = login_plugin.get_user()
    print(user)
    hashed = hasher.encrypt(pwd, rounds=800000, salt=user["salt"])

    if (hashed.split('$')[4] == user["pwd"]):
        login_plugin.login_user(user_id)
        return redirect('/')
    else:
        return template('login', errors=[
            'The username or password was wrong.'
        ])


run(app, host='localhost', port=8080)
