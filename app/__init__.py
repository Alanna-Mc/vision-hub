from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy() 

os.makedirs(app.config['PROFILE_PHOTO_FOLDER'], exist_ok=True)

db.init_app(app)
migrate.init_app(app, db)
login.init_app(app)

from app import routes, models
from app.admin import routes

