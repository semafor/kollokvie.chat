from kollokvie_chat.models import Message, Room, User
from bottle import (abort, template, request, redirect, static_file,
                    response)
from datetime import datetime
from cgi import escape

db = None


def get_login_plugin(request):
    '''Returns login plugin from a request.'''
    for plugin in request.app.plugins:
        # Not very pythonic
        if "get_user" in dir(plugin):
            return plugin
    return None


def render(tpl, **kwargs):
    '''Renders a template.'''
    kwargs['template_lookup'] = [request.app.config['TMPL_FOLDER']]
    return template(tpl, **kwargs)


def signup_get():
    '''Handler for /signup.'''
    # user = get_login_plugin(request).get_user()
    return render('signup_not_logged_in')


def signup_post():
    '''Handler for /signup when used submitted the form.'''
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
        redirect('/')


def signup_error(errors, **kwargs):
    '''Handler for /signup when an erroneous form was submitted.'''
    return render('signup_not_logged_in', errors=errors, **kwargs)


def index():
    '''Handler for /. Either the room selector or a specific room (todo).'''
    user = get_login_plugin(request).get_user()
    if user is None:
        redirect('/login')

    return template('index',
                    template_lookup=[request.app.config['TMPL_FOLDER']],
                    name=user.name,
                    rooms=Room.get_all(order_by='rid'))


def logout():
    '''Handler for /logout.'''
    get_login_plugin(request).logout_user()
    redirect('/')


def login():
    '''Handler for /login.'''
    return template('login',
                    template_lookup=[request.app.config['TMPL_FOLDER']])


def do_login():
    '''Handler for /login when user submitted a form.'''
    email = str(request.POST.get('email'))
    pwd = str(request.POST.get('password'))
    user = User.get(email)

    if user is None or not user.compare_password(pwd):
        return template('login', errors=[
            'We found no account for the given credentials.'
        ], template_lookup=[request.app.config['TMPL_FOLDER']],
            email=email)

    get_login_plugin(request).login_user(email)
    redirect('/')


def room(rid=None, slug=None):
    '''Handler for /room/id/slug.'''
    if slug is None:
        redirect('/')

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        redirect('/')

    room = Room.get(rid)

    if not room.contains_user(user):
        room.add(user)

    return template(
        'room', template_lookup=[request.app.config['TMPL_FOLDER']],
        room=room, rooms=Room.get_all(order_by='name'), user=user,
        messages=room.get_messages(),
    )


def room_part(rid=None, slug=None):
    '''Handler for when user exits /room/id/slug.'''
    if slug is None or rid is None:
        abort(404, "Room not found.")

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        redirect('/')

    room = Room.get(rid)
    room.remove(user)
    redirect('/')


def room_say(rid=None, slug=None):
    '''Handler for when user speaks to /room/id/slug.'''
    if slug is None or rid is None:
        abort(404, "Room not found.")

    user = get_login_plugin(request).get_user()

    # TODO: replace with decorator
    if user is None:
        redirect('/')

    message = request.forms.get('message')
    msg = Message()
    msg.content = message
    msg.date = datetime.now()
    msg.save()

    room = Room.get(rid)
    if slug != room.slug:
        abort(404, "Room not found.")

    room.add(msg)
    user.add(msg)

    from_js = False
    client_id = request.forms.get('client_id')
    if client_id:
        msg.client_id = client_id
        from_js = True

    if from_js:
        return template(
            'message_js', template_lookup=[request.app.config['TMPL_FOLDER']],
            message=msg
        )
    else:
        redirect(room.get_url())


def messages_from(rid=None, slug=None, msg_id=None):
    '''Handler for when user polls for messages.'''
    if slug is None or rid is None:
        abort(404, "Room not found.")

    user = get_login_plugin(request).get_user()
    if user is None:
        redirect('/')

    room = Room.get(rid)
    if slug != room.slug:
        abort(404, "Room not found.")

    messages = room.get_messages_from(msg_id)
    response.set_header('messages', len(messages))
    return template(
        'messages_js', template_lookup=[request.app.config['TMPL_FOLDER']],
        messages=messages
    )


def room_new():
    '''Handler for when user wants to create a new room.'''
    return render('room_new')


def room_new_do():
    '''Handler for when user wants to create a new room.'''
    name = request.forms.get('name')

    if name is None or name is '':
        errors = ['Please enter a room name.']
        return render('room_new', errors=errors)

    user = get_login_plugin(request).get_user()
    if user is None:
        redirect('/')

    room = Room.get_by_name(name)
    if room is not None:
        errors = ['Room already exist, please enter a different name.']
        return render('room_new', errors=errors)

    room = Room()
    room.name = name
    room.slug = name
    room.display_name = name
    room.topic = 'Welcome to %s' % name
    room.save()

    redirect(room.get_url())


def javascripts(filename):
    return static_file(filename, root='%s/js' %
                       request.app.config['STATIC_FOLDER'])


def stylesheets(filename):
    return static_file(filename, root='%s/css' %
                       request.app.config['STATIC_FOLDER'])


def images(filename):
    return static_file(filename, root='%s/images' %
                       request.app.config['STATIC_FOLDER'])


def fonts(filename):
    return static_file(filename, root='%s/fonts' %
                       request.app.config['STATIC_FOLDER'])
