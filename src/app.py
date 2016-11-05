import kollokvie_chat.database as database
import kollokvie_chat.models as models
import kollokvie_chat.views as views

from bottle import Bottle, run
from bottle_login import LoginPlugin

app = Bottle()
app.config['SECRET_KEY'] = 'secret'
app.config['DATABASE'] = 'kollokvie_chat.db'
app.config['STATIC_FOLDER'] = 'src/kollokvie_chat/static'
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 8080
app.config['TMPL_FOLDER'] = 'src/kollokvie_chat/templates/'

login_plugin = app.install(LoginPlugin())


@login_plugin.load_user
def load_user_by_id(user_id):
    return models.User.get(user_id)


db = database.Database(app.config['DATABASE'])
db.initialize()
views.db = db
models.db = db

app.route('/', ['GET'], views.index)
app.route('/login', ['GET'], views.login)
app.route('/room/new', ['GET'], views.room_new)
app.route('/room/new', ['POST'], views.room_new_do)
app.route('/room/<rid>/<slug>', ['GET'], views.room)
app.route('/room/<rid>/<slug>/part', ['GET'], views.room_part)
app.route('/room/<rid>/<slug>/say', ['POST'], views.room_say)
app.route('/room/<rid>/<slug>/messages/from/<msg_id>', ['GET'],
          views.messages_from)
app.route('/login', ['POST'], views.do_login)
app.route('/logout', ['GET'], views.logout)
app.route('/signup', ['GET'], views.signup_get)
app.route('/signup', ['POST'], views.signup_post)

app.route('/<filename:re:.*\.js>', ['GET'], views.javascripts)
app.route('/<filename:re:.*\.css>', ['GET'], views.stylesheets)
app.route('/<filename:re:.*\.(jpg|jpeg|png|gif|ico)>', ['GET'], views.images)
app.route('/<filename:re:.*\.(eot|ttf|woff|svg|otf)>', ['GET'], views.fonts)

if __name__ == '__main__':
    run(app, host=app.config['HOST'], port=app.config['PORT'], debug=True,
        reloader=True)
