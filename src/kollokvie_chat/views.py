from kollokvie_chat.models import Message, Room, User

from bottle import template, request, redirect, static_file
from datetime import datetime
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

    if User.get(email) is not None:
        errors = ['A user with email %s already exist.' % escape(email)]
        return signup_error(errors, email=email, name=name)

    try:
        user.save()
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
    if user is None:
        return redirect('/login')

    return template('index',
                    template_lookup=['src/kollokvie_chat/templates/'],
                    name=user.name,
                    rooms=Room.get_all(order_by='name'))


def logout():
    get_login_plugin(request).logout_user()
    return redirect('/')


def login():
    return template('login', template_lookup=['src/kollokvie_chat/templates/'])


def do_login():
    email = str(request.POST.get('email'))
    pwd = str(request.POST.get('password'))
    user = User.get(email)

    if user is None or not user.compare_password(pwd):
        return template('login', errors=[
            'We found no account for the given credentials.'
        ], template_lookup=['src/kollokvie_chat/templates/'],
            email=email)

    get_login_plugin(request).login_user(email)
    return redirect('/')


def room(rid=None, slug=None):
    if slug is None:
        return redirect('/')

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        return redirect('/')

    room = Room.get(rid)
    room.add(user)
    return template('room', template_lookup=['src/kollokvie_chat/templates/'],
                    room=room, rooms=Room.get_all(order_by='name'),
                    messages=room.get_messages())


def room_part(rid=None, slug=None):
    if slug is None:
        return redirect('/')

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        return redirect('/')

    room = Room.get(rid)
    room.remove(user)
    return redirect('/')


def room_say(rid=None, slug=None):
    if slug is None or rid is None:
        return redirect('/')

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        return redirect('/')

    message = request.forms.get('message')
    msg = Message()
    msg.content = message
    msg.date = datetime.now()
    msg.save()

    room = Room.get(rid)
    room.add(msg)
    user.add(msg)
    return redirect(room.get_url())


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
