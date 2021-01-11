from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bd834b3cbd17bdd82e7c4e867dcf7bde'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
flask_bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ""
app.config['MAIL_PASSWORD'] = ""
mail = Mail(app)

from Flaskblog import routes
