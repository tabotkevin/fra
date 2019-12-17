from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_mail import Mail
from flask_moment import Moment


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
mail = Mail(app)
moment = Moment(app)

lm = LoginManager()
lm.session_protection = "strong"
lm.login_view = 'auth.login'
lm.init_app(app)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix='/admin')
