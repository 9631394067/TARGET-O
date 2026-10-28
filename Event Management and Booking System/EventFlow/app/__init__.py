from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes'), exist_ok=True)

    from app.auth.routes import auth
    from app.events.routes import events
    from app.bookings.routes import bookings
    from app.admin.routes import admin
    from app.main.routes import main

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(events, url_prefix='/events')
    app.register_blueprint(bookings, url_prefix='/bookings')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(main)

    return app
