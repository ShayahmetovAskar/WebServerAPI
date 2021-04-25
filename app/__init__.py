import os
from flask import Flask, url_for

from .views.auth import auth
from .views.class_views import class_views
from .views.index import index
from .login_manager import login_manager, load_user
from werkzeug.debug import DebuggedApplication
from app import test

root_path = None


def create_app(config_file='settings.py'):
    from .data import db_session
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile(config_file)
    db_session.global_init('app/db/database.db')
    login_manager.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(index)
    app.register_blueprint(class_views)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
    test.test()

    global root_path
    root_path = app.root_path

    return app

