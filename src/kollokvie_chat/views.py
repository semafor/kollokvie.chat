from kollokvie_chat.models import User

from bottle import template, request, redirect, static_file
from bottle_login import LoginPlugin
from html import escape


db = None


def get_login_plugin(request):
    for plugin in request.app.plugins:
        # Not very pythonic
        if "get_user" in dir(plugin):
            return plugin
    return None


def render(tpl, **kwargs):
    kwargs['template_lookup'] = ['src/kollokvie_chat/templates/']
    return template(tpl, **kwargs)


def signup_get():
    # user = get_login_plugin(request).get_user()
    return render('signup_not_logged_in')


def signup_post():
    name = request.forms.get('name')
    email = request.forms.get('email')
    password = request.forms.get('password')

    if password is None or len(password) < 7:
        errors = ['Please enter a password with seven or more characters.']
        return signup_error(errors, email=email, name=name)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password, config={'hashing_rounds': 2000})

    if db.get_user(email) is not None:
        errors = ['A user with email %s already exist.' % escape(email)]
        return signup_error(errors, email=email, name=name)

    try:
        db.add_user(user)
    except Exception as e:
        errors = ['Something went wrong: %s' % e]
        return signup_error(errors)
    else:
        get_login_plugin(request).login_user(email)
        return redirect('/')


def signup_error(errors, **kwargs):
    return render('signup_not_logged_in', errors=errors, **kwargs)


def index():
    user = get_login_plugin(request).get_user()
    print(user)
    if user is None:
        return redirect('/login')

    return template('index',
                    template_lookup=['src/kollokvie_chat/templates/'],
                    name=user.name)


def logout():
    get_login_plugin(request).logout_user()
    return redirect('/')


def login():
    return template('login', template_lookup=['src/kollokvie_chat/templates/'])


def do_login():
    email = str(request.POST.get('email'))
    pwd = str(request.POST.get('password'))
    user = db.get_user(email)

    if user is None or not user.compare_password(pwd):
        return template('login', errors=[
            'We found no account for the given credentials.'
        ], template_lookup=['src/kollokvie_chat/templates/'],
            email=email)

    get_login_plugin(request).login_user(email)
    return redirect('/')


def javascripts(filename):
    return static_file(filename, root='%s/js' %
                       request.app.config['STATIC_FOLDER'])


def stylesheets(filename):
    return static_file(filename, root='%s/css' %
                       request.app.config['STATIC_FOLDER'])


def images(filename):
    return static_file(filename, root='%s/img' %
                       request.app.config['STATIC_FOLDER'])


def fonts(filename):
    return static_file(filename, root='%s/fonts' %
                       request.app.config['STATIC_FOLDER'])