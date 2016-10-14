import kollokvie_chat.database as database
import kollokvie_chat.views as views

from bottle import Bottle, run, template, request, redirect
from bottle_login import LoginPlugin

app = Bottle()
app.config['SECRET_KEY'] = 'secret'
app.config['DATABASE'] = 'kollokvie_chat.db'
app.config['STATIC_FOLDER'] = 'src/kollokvie_chat/static'

login_plugin = app.install(LoginPlugin())


@login_plugin.load_user
def load_user_by_id(user_id):
    print('load_user_by_id', db.get_user(user_id))
    return db.get_user(user_id)


db = database.Database(app.config['DATABASE'])
db.initialize()
views.db = db

app.route('/', ['GET'], views.index)
app.route('/login', ['GET'], views.login)
app.route('/login', ['POST'], views.do_login)
app.route('/logout', ['GET'], views.logout)
app.route('/signup', ['GET'], views.signup_get)
app.route('/signup', ['POST'], views.signup_post)

app.route('/<filename:re:.*\.js>', ['GET'], views.javascripts)
app.route('/<filename:re:.*\.css>', ['GET'], views.stylesheets)
app.route('/<filename:re:.*\.(jpg|png|gif|ico)>', ['GET'], views.images)
app.route('/<filename:re:.*\.(eot|ttf|woff|svg)>', ['GET'], views.fonts)

if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
